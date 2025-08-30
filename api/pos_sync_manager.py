# Advanced POS Synchronization Manager - Stage 4
import logging
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.db import transaction, models
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class POSSyncManager:
    """Advanced POS synchronization with bidirectional sync, conflict resolution, and multi-POS support"""
    
    def __init__(self):
        self.retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=1
        )
        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)
        self.session = requests.Session()
        self.session.mount("http://", self.adapter)
        self.session.mount("https://", self.adapter)
    
    def sync_menu_bidirectional(self, menu_id: int, pos_integration_id: int) -> Dict:
        """Perform bidirectional synchronization between menu and POS system"""
        from .models import Menu, POSIntegration, MenuItemPOSSync, POSUpdateLog
        
        try:
            menu = Menu.objects.get(menu_id=menu_id)
            pos_integration = POSIntegration.objects.get(id=pos_integration_id)
            
            sync_result = {
                'status': 'success',
                'menu_to_pos_updates': 0,
                'pos_to_menu_updates': 0,
                'conflicts_resolved': 0,
                'errors': [],
                'timestamp': timezone.now().isoformat()
            }
            
            # Phase 1: Get current state from both systems
            menu_items = self._get_menu_items_with_sync_data(menu)
            pos_items = self._fetch_pos_items(pos_integration)
            
            if not pos_items:
                sync_result['errors'].append('Failed to fetch POS items')
                return sync_result
            
            # Phase 2: Detect conflicts and resolve them
            conflicts = self._detect_sync_conflicts(menu_items, pos_items)
            if conflicts:
                resolved_conflicts = self._resolve_conflicts(conflicts, pos_integration.conflict_resolution_strategy)
                sync_result['conflicts_resolved'] = len(resolved_conflicts)
                
                # Log conflicts for audit
                for conflict in resolved_conflicts:
                    POSUpdateLog.objects.create(
                        pos_integration=pos_integration,
                        operation='conflict_resolution',
                        details=json.dumps(conflict),
                        success=True
                    )
            
            # Phase 3: Sync menu changes to POS
            menu_to_pos_updates = self._sync_menu_to_pos(menu_items, pos_items, pos_integration)
            sync_result['menu_to_pos_updates'] = len(menu_to_pos_updates)
            
            # Phase 4: Sync POS changes to menu
            pos_to_menu_updates = self._sync_pos_to_menu(pos_items, menu_items, menu, pos_integration)
            sync_result['pos_to_menu_updates'] = len(pos_to_menu_updates)
            
            # Phase 5: Update sync timestamps and status
            self._update_sync_metadata(menu, pos_integration, sync_result)
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Bidirectional sync failed for menu {menu_id}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
    
    def _get_menu_items_with_sync_data(self, menu) -> Dict:
        """Get menu items with their POS sync metadata"""
        from .models import MenuItemPOSSync
        
        items = {}
        for item in menu.items.all():
            sync_data = MenuItemPOSSync.objects.filter(menu_item=item).first()
            items[item.item_id] = {
                'item': item,
                'sync_data': sync_data,
                'last_modified': item.updated_at if hasattr(item, 'updated_at') else item.created_at,
                'pos_id': sync_data.pos_item_id if sync_data else None,
                'last_pos_sync': sync_data.last_pos_update if sync_data else None
            }
        return items
    
    def _fetch_pos_items(self, pos_integration) -> Optional[Dict]:
        """Fetch items from POS system with retry logic"""
        try:
            headers = self._get_pos_headers(pos_integration)
            url = self._build_pos_url(pos_integration, 'items')
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse response based on POS system type
            data = response.json()
            return self._normalize_pos_items(data, pos_integration.pos_system)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch POS items: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing POS response: {str(e)}")
            return None
    
    def _normalize_pos_items(self, raw_data: Dict, pos_system: str) -> Dict:
        """Normalize POS item data across different POS systems"""
        normalized = {}
        
        if pos_system == 'square':
            items = raw_data.get('objects', [])
            for item in items:
                item_data = item.get('item_data', {})
                variations = item_data.get('variations', [])
                
                for variation in variations:
                    var_data = variation.get('item_variation_data', {})
                    price_money = var_data.get('price_money', {})
                    
                    normalized[variation['id']] = {
                        'id': variation['id'],
                        'name': item_data.get('name', ''),
                        'description': item_data.get('description', ''),
                        'price': float(price_money.get('amount', 0)) / 100,  # Square uses cents
                        'currency': price_money.get('currency', 'USD'),
                        'available': not item_data.get('is_deleted', False),
                        'category': item_data.get('category_id'),
                        'updated_at': item.get('updated_at'),
                        'raw_data': item
                    }
        
        elif pos_system == 'toast':
            items = raw_data.get('menuItems', [])
            for item in items:
                normalized[item['guid']] = {
                    'id': item['guid'],
                    'name': item.get('name', ''),
                    'description': item.get('description', ''),
                    'price': float(item.get('price', 0)),
                    'currency': 'USD',  # Toast typically uses USD
                    'available': not item.get('deleted', False),
                    'category': item.get('menuGroupGuid'),
                    'updated_at': item.get('modifiedDate'),
                    'raw_data': item
                }
        
        elif pos_system == 'lightspeed':
            items = raw_data.get('Item', [])
            for item in items:
                item_id = str(item.get('itemID'))
                normalized[item_id] = {
                    'id': item_id,
                    'name': item.get('description', ''),
                    'description': item.get('longDescription', ''),
                    'price': float(item.get('Prices', {}).get('ItemPrice', [{}])[0].get('amount', 0)),
                    'currency': 'USD',
                    'available': item.get('archived') != 'true',
                    'category': item.get('categoryID'),
                    'updated_at': item.get('timeStamp'),
                    'raw_data': item
                }
        
        elif pos_system == 'shopify':
            products = raw_data.get('products', [])
            for product in products:
                for variant in product.get('variants', []):
                    normalized[str(variant['id'])] = {
                        'id': str(variant['id']),
                        'name': f"{product.get('title', '')} - {variant.get('title', '')}",
                        'description': product.get('body_html', ''),
                        'price': float(variant.get('price', 0)),
                        'currency': 'USD',
                        'available': variant.get('inventory_quantity', 0) > 0,
                        'category': product.get('product_type'),
                        'updated_at': variant.get('updated_at'),
                        'raw_data': {'product': product, 'variant': variant}
                    }
        
        else:  # Generic POS system
            items = raw_data.get('items', [])
            for item in items:
                item_id = str(item.get('id'))
                normalized[item_id] = {
                    'id': item_id,
                    'name': item.get('name', ''),
                    'description': item.get('description', ''),
                    'price': float(item.get('price', 0)),
                    'currency': item.get('currency', 'USD'),
                    'available': item.get('available', True),
                    'category': item.get('category'),
                    'updated_at': item.get('updated_at'),
                    'raw_data': item
                }
        
        return normalized
    
    def _detect_sync_conflicts(self, menu_items: Dict, pos_items: Dict) -> List[Dict]:
        """Detect synchronization conflicts between menu and POS data"""
        conflicts = []
        
        for menu_item_id, menu_data in menu_items.items():
            pos_id = menu_data['pos_id']
            if not pos_id or pos_id not in pos_items:
                continue
            
            menu_item = menu_data['item']
            pos_item = pos_items[pos_id]
            
            # Check for price conflicts
            if abs(float(menu_item.price) - pos_item['price']) > 0.01:
                conflicts.append({
                    'type': 'price_mismatch',
                    'menu_item_id': menu_item_id,
                    'pos_item_id': pos_id,
                    'menu_value': float(menu_item.price),
                    'pos_value': pos_item['price'],
                    'menu_updated': menu_data['last_modified'],
                    'pos_updated': pos_item.get('updated_at')
                })
            
            # Check for name conflicts
            if menu_item.name != pos_item['name']:
                conflicts.append({
                    'type': 'name_mismatch',
                    'menu_item_id': menu_item_id,
                    'pos_item_id': pos_id,
                    'menu_value': menu_item.name,
                    'pos_value': pos_item['name'],
                    'menu_updated': menu_data['last_modified'],
                    'pos_updated': pos_item.get('updated_at')
                })
            
            # Check for availability conflicts
            if menu_item.available != pos_item['available']:
                conflicts.append({
                    'type': 'availability_mismatch',
                    'menu_item_id': menu_item_id,
                    'pos_item_id': pos_id,
                    'menu_value': menu_item.available,
                    'pos_value': pos_item['available'],
                    'menu_updated': menu_data['last_modified'],
                    'pos_updated': pos_item.get('updated_at')
                })
        
        return conflicts
    
    def _resolve_conflicts(self, conflicts: List[Dict], strategy: str) -> List[Dict]:
        """Resolve synchronization conflicts based on strategy"""
        resolved = []
        
        for conflict in conflicts:
            resolution = {
                'conflict': conflict,
                'strategy': strategy,
                'resolution': None,
                'timestamp': timezone.now().isoformat()
            }
            
            if strategy == 'pos_wins':
                resolution['resolution'] = 'use_pos_value'
                resolution['winning_value'] = conflict['pos_value']
                
            elif strategy == 'menu_wins':
                resolution['resolution'] = 'use_menu_value'
                resolution['winning_value'] = conflict['menu_value']
                
            elif strategy == 'latest_wins':
                menu_time = conflict.get('menu_updated')
                pos_time = conflict.get('pos_updated')
                
                if menu_time and pos_time:
                    menu_dt = datetime.fromisoformat(menu_time.replace('Z', '+00:00')) if isinstance(menu_time, str) else menu_time
                    pos_dt = datetime.fromisoformat(pos_time.replace('Z', '+00:00')) if isinstance(pos_time, str) else datetime.now()
                    
                    if menu_dt > pos_dt:
                        resolution['resolution'] = 'use_menu_value'
                        resolution['winning_value'] = conflict['menu_value']
                    else:
                        resolution['resolution'] = 'use_pos_value'
                        resolution['winning_value'] = conflict['pos_value']
                else:
                    # Default to POS if timestamps are unclear
                    resolution['resolution'] = 'use_pos_value'
                    resolution['winning_value'] = conflict['pos_value']
            
            resolved.append(resolution)
        
        return resolved
    
    def _sync_menu_to_pos(self, menu_items: Dict, pos_items: Dict, pos_integration) -> List[Dict]:
        """Sync menu changes to POS system"""
        updates = []
        
        for menu_item_id, menu_data in menu_items.items():
            menu_item = menu_data['item']
            pos_id = menu_data['pos_id']
            
            # Skip if no POS mapping exists
            if not pos_id:
                continue
            
            # Check if item needs updating in POS
            if pos_id in pos_items:
                pos_item = pos_items[pos_id]
                update_needed = self._check_pos_update_needed(menu_item, pos_item, menu_data)
                
                if update_needed:
                    success = self._update_pos_item(menu_item, pos_id, pos_integration)
                    if success:
                        updates.append({
                            'action': 'update',
                            'menu_item_id': menu_item_id,
                            'pos_item_id': pos_id,
                            'timestamp': timezone.now().isoformat()
                        })
        
        return updates
    
    def _sync_pos_to_menu(self, pos_items: Dict, menu_items: Dict, menu, pos_integration) -> List[Dict]:
        """Sync POS changes to menu system"""
        from .models import MenuItem, MenuCategory, MenuItemPOSSync
        
        updates = []
        
        # Map POS items to menu items
        pos_to_menu = {data['pos_id']: item_id for item_id, data in menu_items.items() if data['pos_id']}
        
        for pos_id, pos_item in pos_items.items():
            if pos_id in pos_to_menu:
                # Update existing menu item
                menu_item_id = pos_to_menu[pos_id]
                menu_data = menu_items[menu_item_id]
                menu_item = menu_data['item']
                
                update_needed = self._check_menu_update_needed(pos_item, menu_item, menu_data)
                
                if update_needed:
                    self._update_menu_item_from_pos(menu_item, pos_item)
                    updates.append({
                        'action': 'update',
                        'menu_item_id': menu_item_id,
                        'pos_item_id': pos_id,
                        'timestamp': timezone.now().isoformat()
                    })
            
            else:
                # Create new menu item from POS
                if pos_integration.auto_create_items:
                    new_item = self._create_menu_item_from_pos(pos_item, menu)
                    if new_item:
                        # Create sync record
                        MenuItemPOSSync.objects.create(
                            menu_item=new_item,
                            pos_item_id=pos_id,
                            last_pos_update=timezone.now(),
                            pos_data=json.dumps(pos_item['raw_data'])
                        )
                        
                        updates.append({
                            'action': 'create',
                            'menu_item_id': new_item.item_id,
                            'pos_item_id': pos_id,
                            'timestamp': timezone.now().isoformat()
                        })
        
        return updates
    
    def _check_pos_update_needed(self, menu_item, pos_item, menu_data) -> bool:
        """Check if POS item needs updating from menu"""
        last_sync = menu_data['last_pos_sync']
        last_modified = menu_data['last_modified']
        
        # If never synced or menu updated after last sync
        if not last_sync or last_modified > last_sync:
            return True
        
        # Check for actual differences
        if abs(float(menu_item.price) - pos_item['price']) > 0.01:
            return True
        
        if menu_item.name != pos_item['name']:
            return True
        
        if menu_item.available != pos_item['available']:
            return True
        
        return False
    
    def _check_menu_update_needed(self, pos_item, menu_item, menu_data) -> bool:
        """Check if menu item needs updating from POS"""
        pos_updated = pos_item.get('updated_at')
        last_sync = menu_data['last_pos_sync']
        
        # If POS updated after last sync
        if pos_updated and last_sync:
            try:
                pos_dt = datetime.fromisoformat(pos_updated.replace('Z', '+00:00')) if isinstance(pos_updated, str) else pos_updated
                sync_dt = last_sync if isinstance(last_sync, datetime) else datetime.fromisoformat(last_sync)
                
                if pos_dt > sync_dt:
                    return True
            except (ValueError, AttributeError):
                pass
        
        # Check for actual differences
        if abs(float(menu_item.price) - pos_item['price']) > 0.01:
            return True
        
        if menu_item.name != pos_item['name']:
            return True
        
        if menu_item.available != pos_item['available']:
            return True
        
        return False
    
    def _update_pos_item(self, menu_item, pos_id: str, pos_integration) -> bool:
        """Update item in POS system"""
        try:
            headers = self._get_pos_headers(pos_integration)
            url = self._build_pos_url(pos_integration, f'items/{pos_id}')
            
            # Build update payload based on POS system
            payload = self._build_pos_update_payload(menu_item, pos_integration.pos_system)
            
            response = self.session.put(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            # Update sync record
            self._update_pos_sync_record(menu_item, pos_id, timezone.now())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update POS item {pos_id}: {str(e)}")
            return False
    
    def _update_menu_item_from_pos(self, menu_item, pos_item):
        """Update menu item from POS data"""
        from .models import MenuItemPOSSync
        
        try:
            with transaction.atomic():
                # Update menu item fields
                menu_item.name = pos_item['name']
                menu_item.description = pos_item.get('description', menu_item.description)
                menu_item.price = pos_item['price']
                menu_item.available = pos_item['available']
                menu_item.save()
                
                # Update sync record
                sync_record = MenuItemPOSSync.objects.filter(menu_item=menu_item).first()
                if sync_record:
                    sync_record.last_pos_update = timezone.now()
                    sync_record.pos_data = json.dumps(pos_item['raw_data'])
                    sync_record.save()
                
        except Exception as e:
            logger.error(f"Failed to update menu item {menu_item.item_id}: {str(e)}")
    
    def _create_menu_item_from_pos(self, pos_item, menu):
        """Create new menu item from POS data"""
        from .models import MenuItem, MenuCategory
        
        try:
            # Find or create category
            category = None
            if pos_item.get('category'):
                category, _ = MenuCategory.objects.get_or_create(
                    menu=menu,
                    name=f"POS Category {pos_item['category']}",
                    defaults={'description': 'Auto-created from POS'}
                )
            
            # Create menu item
            menu_item = MenuItem.objects.create(
                menu=menu,
                category=category,
                name=pos_item['name'],
                description=pos_item.get('description', ''),
                price=pos_item['price'],
                currency=pos_item.get('currency', 'USD'),
                available=pos_item['available']
            )
            
            return menu_item
            
        except Exception as e:
            logger.error(f"Failed to create menu item from POS: {str(e)}")
            return None
    
    def _get_pos_headers(self, pos_integration) -> Dict:
        """Get authentication headers for POS system"""
        headers = {'Content-Type': 'application/json'}
        
        if pos_integration.pos_system == 'square':
            headers['Authorization'] = f'Bearer {pos_integration.api_key}'
            headers['Square-Version'] = '2023-12-13'
            
        elif pos_integration.pos_system == 'toast':
            headers['Authorization'] = f'Toast {pos_integration.api_key}'
            
        elif pos_integration.pos_system == 'lightspeed':
            headers['Authorization'] = f'Bearer {pos_integration.api_key}'
            
        elif pos_integration.pos_system == 'shopify':
            headers['X-Shopify-Access-Token'] = pos_integration.api_key
            
        else:
            headers['Authorization'] = f'Bearer {pos_integration.api_key}'
        
        return headers
    
    def _build_pos_url(self, pos_integration, endpoint: str) -> str:
        """Build POS API URL"""
        base_urls = {
            'square': 'https://connect.squareup.com/v2/catalog',
            'toast': f'https://api.toasttab.com/{pos_integration.location_id}/menus',
            'lightspeed': f'https://api.lightspeedapp.com/API/Account/{pos_integration.location_id}',
            'shopify': f'https://{pos_integration.store_domain}.myshopify.com/admin/api/2023-10',
            'generic': pos_integration.api_url
        }
        
        base_url = base_urls.get(pos_integration.pos_system, pos_integration.api_url)
        return f"{base_url}/{endpoint}"
    
    def _build_pos_update_payload(self, menu_item, pos_system: str) -> Dict:
        """Build update payload for specific POS system"""
        if pos_system == 'square':
            return {
                "object": {
                    "type": "ITEM",
                    "id": menu_item.pos_sync.pos_item_id if hasattr(menu_item, 'pos_sync') else None,
                    "item_data": {
                        "name": menu_item.name,
                        "description": menu_item.description or "",
                        "variations": [{
                            "type": "ITEM_VARIATION",
                            "item_variation_data": {
                                "name": "Regular",
                                "price_money": {
                                    "amount": int(float(menu_item.price) * 100),
                                    "currency": menu_item.currency
                                }
                            }
                        }]
                    }
                }
            }
        
        elif pos_system == 'toast':
            return {
                "name": menu_item.name,
                "description": menu_item.description or "",
                "price": float(menu_item.price),
                "deleted": not menu_item.available
            }
        
        else:  # Generic
            return {
                "name": menu_item.name,
                "description": menu_item.description or "",
                "price": float(menu_item.price),
                "currency": menu_item.currency,
                "available": menu_item.available
            }
    
    def _update_pos_sync_record(self, menu_item, pos_id: str, sync_time):
        """Update POS sync record"""
        from .models import MenuItemPOSSync
        
        sync_record, created = MenuItemPOSSync.objects.get_or_create(
            menu_item=menu_item,
            defaults={'pos_item_id': pos_id}
        )
        
        sync_record.last_pos_update = sync_time
        sync_record.save()
    
    def _update_sync_metadata(self, menu, pos_integration, sync_result):
        """Update synchronization metadata"""
        from .models import POSUpdateLog
        
        # Create sync log entry
        POSUpdateLog.objects.create(
            pos_integration=pos_integration,
            operation='bidirectional_sync',
            details=json.dumps(sync_result),
            success=sync_result['status'] == 'success'
        )
        
        # Update cache with sync status
        cache_key = f"pos_sync_status_{menu.menu_id}_{pos_integration.id}"
        cache.set(cache_key, sync_result, timeout=300)  # 5 minutes
    
    async def schedule_sync_job(self, menu_id: int, pos_integration_id: int, interval_minutes: int = 15):
        """Schedule automatic synchronization job"""
        while True:
            try:
                logger.info(f"Starting scheduled sync for menu {menu_id}")
                result = self.sync_menu_bidirectional(menu_id, pos_integration_id)
                
                if result['status'] == 'success':
                    logger.info(f"Sync completed: {result['menu_to_pos_updates']} menu→POS, {result['pos_to_menu_updates']} POS→menu")
                else:
                    logger.error(f"Sync failed: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                logger.error(f"Scheduled sync error: {str(e)}")
            
            # Wait for next sync
            await asyncio.sleep(interval_minutes * 60)


class WebhookManager:
    """Manage POS webhooks for real-time updates"""
    
    def __init__(self):
        self.sync_manager = POSSyncManager()
    
    def setup_pos_webhooks(self, pos_integration) -> bool:
        """Setup webhooks for POS system"""
        try:
            webhook_url = self._get_webhook_url(pos_integration)
            
            if pos_integration.pos_system == 'square':
                return self._setup_square_webhooks(pos_integration, webhook_url)
            elif pos_integration.pos_system == 'toast':
                return self._setup_toast_webhooks(pos_integration, webhook_url)
            elif pos_integration.pos_system == 'shopify':
                return self._setup_shopify_webhooks(pos_integration, webhook_url)
            else:
                logger.warning(f"Webhook setup not implemented for {pos_integration.pos_system}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup webhooks: {str(e)}")
            return False
    
    def _setup_square_webhooks(self, pos_integration, webhook_url: str) -> bool:
        """Setup Square webhooks"""
        headers = {
            'Authorization': f'Bearer {pos_integration.api_key}',
            'Content-Type': 'application/json',
            'Square-Version': '2023-12-13'
        }
        
        webhook_data = {
            "subscription": {
                "name": f"Menu Sync - {pos_integration.id}",
                "event_types": [
                    "catalog.version.updated",
                    "inventory.count.updated"
                ],
                "notification_url": webhook_url,
                "api_version": "2023-12-13"
            }
        }
        
        try:
            response = requests.post(
                'https://connect.squareup.com/v2/webhooks/subscriptions',
                headers=headers,
                json=webhook_data,
                timeout=30
            )
            response.raise_for_status()
            
            webhook_response = response.json()
            pos_integration.webhook_id = webhook_response['subscription']['id']
            pos_integration.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Square webhook setup failed: {str(e)}")
            return False
    
    def _setup_shopify_webhooks(self, pos_integration, webhook_url: str) -> bool:
        """Setup Shopify webhooks"""
        headers = {
            'X-Shopify-Access-Token': pos_integration.api_key,
            'Content-Type': 'application/json'
        }
        
        webhook_data = {
            "webhook": {
                "topic": "products/update",
                "address": webhook_url,
                "format": "json"
            }
        }
        
        try:
            url = f"https://{pos_integration.store_domain}.myshopify.com/admin/api/2023-10/webhooks.json"
            response = requests.post(url, headers=headers, json=webhook_data, timeout=30)
            response.raise_for_status()
            
            webhook_response = response.json()
            pos_integration.webhook_id = webhook_response['webhook']['id']
            pos_integration.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Shopify webhook setup failed: {str(e)}")
            return False
    
    def _get_webhook_url(self, pos_integration) -> str:
        """Generate webhook URL for POS integration"""
        base_url = getattr(settings, 'WEBHOOK_BASE_URL', 'https://your-domain.com')
        return f"{base_url}/api/v1/pos-webhooks/{pos_integration.id}/"
    
    def process_webhook(self, pos_integration_id: int, webhook_data: Dict) -> Dict:
        """Process incoming webhook from POS system"""
        from .models import POSIntegration, POSUpdateLog
        
        try:
            pos_integration = POSIntegration.objects.get(id=pos_integration_id)
            
            # Log webhook receipt
            POSUpdateLog.objects.create(
                pos_integration=pos_integration,
                operation='webhook_received',
                details=json.dumps(webhook_data),
                success=True
            )
            
            # Process based on POS system
            if pos_integration.pos_system == 'square':
                return self._process_square_webhook(pos_integration, webhook_data)
            elif pos_integration.pos_system == 'shopify':
                return self._process_shopify_webhook(pos_integration, webhook_data)
            else:
                return self._process_generic_webhook(pos_integration, webhook_data)
                
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_square_webhook(self, pos_integration, webhook_data: Dict) -> Dict:
        """Process Square webhook"""
        event_type = webhook_data.get('type')
        
        if event_type == 'catalog.version.updated':
            # Trigger menu sync for all menus using this POS integration
            from .models import Menu
            
            menus = Menu.objects.filter(
                items__menuitemposssync__pos_item_id__isnull=False
            ).distinct()
            
            for menu in menus:
                # Trigger async sync
                result = self.sync_manager.sync_menu_bidirectional(menu.menu_id, pos_integration.id)
                logger.info(f"Webhook triggered sync for menu {menu.menu_id}: {result['status']}")
            
            return {'status': 'processed', 'synced_menus': menus.count()}
        
        return {'status': 'ignored', 'reason': f'Unhandled event type: {event_type}'}
    
    def _process_shopify_webhook(self, pos_integration, webhook_data: Dict) -> Dict:
        """Process Shopify webhook"""
        # Shopify sends product update data directly
        product_id = webhook_data.get('id')
        
        if product_id:
            # Find affected menus and trigger sync
            from .models import Menu, MenuItemPOSSync
            
            synced_items = MenuItemPOSSync.objects.filter(
                pos_item_id__contains=str(product_id)
            )
            
            affected_menus = set()
            for sync_item in synced_items:
                affected_menus.add(sync_item.menu_item.menu)
            
            for menu in affected_menus:
                result = self.sync_manager.sync_menu_bidirectional(menu.menu_id, pos_integration.id)
                logger.info(f"Webhook triggered sync for menu {menu.menu_id}: {result['status']}")
            
            return {'status': 'processed', 'synced_menus': len(affected_menus)}
        
        return {'status': 'ignored', 'reason': 'No product ID found'}
    
    def _process_generic_webhook(self, pos_integration, webhook_data: Dict) -> Dict:
        """Process generic webhook"""
        # Trigger sync for all associated menus
        from .models import Menu
        
        menus = Menu.objects.filter(
            items__menuitemposssync__pos_item_id__isnull=False
        ).distinct()
        
        for menu in menus:
            result = self.sync_manager.sync_menu_bidirectional(menu.menu_id, pos_integration.id)
            logger.info(f"Generic webhook triggered sync for menu {menu.menu_id}: {result['status']}")
        
        return {'status': 'processed', 'synced_menus': menus.count()}