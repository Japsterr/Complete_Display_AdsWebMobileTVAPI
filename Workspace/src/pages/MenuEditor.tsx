import React, { useEffect, useState } from 'react';
import { Box, Button, Heading, Input, FormControl, FormLabel, VStack, HStack, Textarea, Select, Image } from '@chakra-ui/react';
import { createMenu, fetchMenu, updateMenu, createMenuCategory, createMenuItem, patchMenuItem, deleteMenuItem, updateMenuCategory, deleteMenuCategory, reorderMenu } from '../services/api';
import { useParams } from 'react-router-dom';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';

export default function MenuEditor(){
  const { id } = useParams();
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState<any[]>([]);
  const [items, setItems] = useState<any[]>([]);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newItem, setNewItem] = useState({ name: '', description: '', price: '', currency: 'ZAR', category: '' });
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  

  useEffect(()=>{
    if(id && id !== 'new'){
      (async ()=>{
        setLoading(true);
        const m = await fetchMenu(Number(id));
        setName(m.name || '');
  setCategories(m.categories || []);
  setItems(m.items || []);
        setLoading(false);
      })();
    }
  }, [id]);

  const save = async () => {
    setLoading(true);
    if(id && id !== 'new'){
      await updateMenu(Number(id), { name });
    } else {
      await createMenu({ name });
    }
    setLoading(false);
    window.location.href = '/menus';
  };

  const addCategory = async () => {
    if(!newCategoryName) return;
    setLoading(true);
    const payload = { menu: Number(id), name: newCategoryName, order: categories.length };
    const cat = await createMenuCategory(payload);
    setCategories(prev=>[...prev, cat]);
    setNewCategoryName('');
    setLoading(false);
  };

  const updateCategoryName = async (categoryId: number, name: string) => {
    setLoading(true);
    const updated = await updateMenuCategory(categoryId, { name });
    setCategories(prev => prev.map(c => c.category_id === updated.category_id ? updated : c));
    setLoading(false);
  };

  const deleteCategory = async (categoryId: number) => {
    if(!confirm('Delete this category? This will orphan or remove items.')) return;
    setLoading(true);
    await deleteMenuCategory(categoryId);
    setCategories(prev => prev.filter(c => c.category_id !== categoryId));
    setItems(prev => prev.map(it => it.category === categoryId ? { ...it, category: null } : it));
    setLoading(false);
  };

  const moveCategory = async (categoryId: number, dir: number) => {
    const idx = categories.findIndex(c=>c.category_id===categoryId);
    if(idx < 0) return;
    const newOrder = [...categories];
    const target = idx + dir;
    if(target < 0 || target >= newOrder.length) return;
    // swap orders
    const a = newOrder[idx];
    newOrder[idx] = newOrder[target];
    newOrder[target] = a;
    // update local state and persist orders
    setCategories(newOrder);
    // persist order values
    for(let i=0;i<newOrder.length;i++){
      try{ await updateMenuCategory(newOrder[i].category_id, { order: i }); }catch(e){ }
    }
  };

  const addItem = async () => {
    if(!newItem.name) return;
    setLoading(true);
    const fd = new FormData();
    fd.append('menu', String(id));
    fd.append('name', newItem.name);
    fd.append('description', newItem.description || '');
    fd.append('price', newItem.price || '0');
    fd.append('currency', newItem.currency || 'ZAR');
    if(newItem.category) fd.append('category', String(newItem.category));
    if(imageFile) fd.append('image', imageFile, imageFile.name);
    const it = await createMenuItem(fd, (p)=> setUploadProgress(p));
    setItems(prev=>[...prev, it]);
    setUploadProgress(null);
    setNewItem({ name: '', description: '', price: '', currency: 'ZAR', category: '' });
    setImageFile(null);
    setLoading(false);
  };

  // DnD onDragEnd handler for both categories and items
  const onDragEnd = async (result: DropResult) => {
    const { source, destination, type } = result;
    if (!destination) return; // dropped outside

    if (type === 'CATEGORY') {
      const srcIdx = source.index;
      const dstIdx = destination.index;
      if (srcIdx === dstIdx) return;
      const newCats = Array.from(categories);
      const [moved] = newCats.splice(srcIdx, 1);
      newCats.splice(dstIdx, 0, moved);
      setCategories(newCats);

      // Build payload for categories
      const categoriesPayload = newCats.map((c, i) => ({ category_id: c.category_id, order: i }));
      // Also include current items ordering to avoid clobbering
      const itemsPayload = items.map((it, i) => ({ item_id: it.item_id, category_id: it.category || null, order: i }));
      try {
        await reorderMenu(Number(id), { categories: categoriesPayload, items: itemsPayload });
      } catch (e) {
        // Best-effort: ignore failures for now
      }
    } else {
      // items - moving between category droppables
      const srcCatId = source.droppableId === 'ungrouped' ? null : Number(source.droppableId.replace('cat-', ''));
      const dstCatId = destination.droppableId === 'ungrouped' ? null : Number(destination.droppableId.replace('cat-', ''));
      const srcIndex = source.index;
      const dstIndex = destination.index;

      // Build per-category lists
      const itemsByCategory: Record<string, any[]> = {};
      const allCatIds = ['ungrouped', ...categories.map(c => `cat-${c.category_id}`)];
      for (const cid of allCatIds) itemsByCategory[cid] = [];
      for (const it of items) {
        const key = it.category ? `cat-${it.category}` : 'ungrouped';
        itemsByCategory[key].push(it);
      }

      // Remove from source
      const srcKey = srcCatId ? `cat-${srcCatId}` : 'ungrouped';
      const dstKey = dstCatId ? `cat-${dstCatId}` : 'ungrouped';
      const [moved] = itemsByCategory[srcKey].splice(srcIndex, 1);
      // assign new category
      moved.category = dstCatId;
      itemsByCategory[dstKey].splice(dstIndex, 0, moved);

      // Flatten back to items array in a consistent order: ungrouped first, then categories order
      const newItems: any[] = [];
      for (const it of itemsByCategory['ungrouped']) newItems.push(it);
      for (const c of categories) {
        const key = `cat-${c.category_id}`;
        for (const it of itemsByCategory[key]) newItems.push(it);
      }
      setItems(newItems);

      const itemsPayload = newItems.map((it, i) => ({ item_id: it.item_id, category_id: it.category || null, order: i }));
      const categoriesPayload = categories.map((c, i) => ({ category_id: c.category_id, order: i }));
      try {
        await reorderMenu(Number(id), { categories: categoriesPayload, items: itemsPayload });
      } catch (e) {
        // ignore for now
      }
    }
  };

  // removed native category drag handlers in favor of @hello-pangea/dnd

  const editItem = async (itemId: number, payload: any) => {
    setLoading(true);
    const updated = await patchMenuItem(itemId, payload);
    setItems(prev => prev.map(it => it.item_id === updated.item_id ? updated : it));
    setLoading(false);
  };

  const removeItem = async (itemId: number) => {
    if(!confirm('Delete this item?')) return;
    setLoading(true);
    await deleteMenuItem(itemId);
    setItems(prev => prev.filter(it => it.item_id !== itemId));
    setLoading(false);
  };

  const moveItem = async (itemId: number, dir: number) => {
    const idx = items.findIndex(i=>i.item_id===itemId);
    if(idx<0) return;
    const newItems = [...items];
    const target = idx + dir;
    if(target < 0 || target >= newItems.length) return;
    const a = newItems[idx]; newItems[idx] = newItems[target]; newItems[target] = a;
    setItems(newItems);
    // persist new orders
    for(let i=0;i<newItems.length;i++){
      try{ await patchMenuItem(newItems[i].item_id, { order: i }); }catch(e){}
    }
  };

  return (
    <Box p={6}>
      <Heading mb={4}>{id === 'new' ? 'Create Menu' : 'Edit Menu'}</Heading>
      <FormControl mb={4}>
        <FormLabel>Name</FormLabel>
        <Input value={name} onChange={(e)=>setName(e.target.value)} />
      </FormControl>

      <VStack align="stretch" spacing={4} mb={6}>
        <Heading size="md">Categories</Heading>
        <HStack>
          <Input placeholder="New category name" value={newCategoryName} onChange={(e)=>setNewCategoryName(e.target.value)} />
          <Button onClick={addCategory} isLoading={loading}>Add</Button>
        </HStack>
        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="categories-droppable" type="CATEGORY">
            {(provided: any) => (
              <VStack align="stretch" ref={provided.innerRef} {...provided.droppableProps}>
                  {categories.map((c, idx) => (
                    <Draggable key={c.category_id} draggableId={`cat-${c.category_id}`} index={idx}>
                      {(prov: any) => (
                        <HStack ref={prov.innerRef} {...prov.draggableProps} {...prov.dragHandleProps} p={2} borderWidth={1} borderRadius={6} justifyContent="space-between">
                        <Box>
                          <Input value={c.name} onChange={(e)=>{
                            const v = e.target.value; setCategories(prev=>prev.map(x=> x.category_id===c.category_id?{...x,name:v}:x));
                          }} onBlur={(e)=>updateCategoryName(c.category_id, e.target.value)} />
                        </Box>
                        <HStack>
                          <Button size="sm" onClick={()=>moveCategory(c.category_id, -1)}>↑</Button>
                          <Button size="sm" onClick={()=>moveCategory(c.category_id, +1)}>↓</Button>
                          <Button size="sm" colorScheme="red" onClick={()=>deleteCategory(c.category_id)}>Delete</Button>
                        </HStack>
                      </HStack>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </VStack>
            )}
          </Droppable>
        </DragDropContext>
      </VStack>

      <VStack align="stretch" spacing={4} mb={6}>
        <Heading size="md">Items</Heading>
  <FormControl>
          <FormLabel>Item name</FormLabel>
          <Input value={newItem.name} onChange={(e)=>setNewItem({...newItem, name: e.target.value})} />
        </FormControl>
        <FormControl>
          <FormLabel>Description</FormLabel>
          <Textarea value={newItem.description} onChange={(e)=>setNewItem({...newItem, description: e.target.value})} />
        </FormControl>
        <HStack>
          <FormControl>
            <FormLabel>Price</FormLabel>
            <Input value={newItem.price} onChange={(e)=>setNewItem({...newItem, price: e.target.value})} />
          </FormControl>
          <FormControl>
            <FormLabel>Currency</FormLabel>
            <Input value={newItem.currency} onChange={(e)=>setNewItem({...newItem, currency: e.target.value})} />
          </FormControl>
          <FormControl>
            <FormLabel>Category</FormLabel>
            <Select value={newItem.category} onChange={(e)=>setNewItem({...newItem, category: e.target.value})} placeholder="Uncategorized">
              {categories.map(c => <option key={c.category_id} value={c.category_id}>{c.name}</option>)}
            </Select>
          </FormControl>
        </HStack>
        <FormControl>
          <FormLabel>Image</FormLabel>
          <Input type="file" onChange={(e:any)=>setImageFile(e.target.files?.[0]||null)} />
        </FormControl>
        <Button onClick={addItem} isLoading={loading}>Add Item</Button>
        {uploadProgress !== null && (
          <Box w="100%" p={2}>
            <Box bg="gray.200" w="100%" h="10px" borderRadius="6px"><Box bg="blue.400" h="10px" w={`${uploadProgress}%`} borderRadius="6px" /></Box>
            <Box fontSize="sm">Uploading: {uploadProgress}%</Box>
          </Box>
        )}

        <DragDropContext onDragEnd={onDragEnd}>
          {/* Render one droppable for ungrouped items and one per category so items can be moved between categories */}
          <HStack align="start" spacing={4}>
            {/* Ungrouped column */}
            <Droppable droppableId="ungrouped" type="ITEM">
              {(provided: any) => (
                <VStack ref={provided.innerRef} {...provided.droppableProps} align="stretch" w="300px" spacing={2}>
                  <Heading size="sm">Uncategorized</Heading>
                  {items.filter(it => !it.category).map((it, index) => (
                    <Draggable key={it.item_id} draggableId={`item-${it.item_id}`} index={index}>
                      {(prov: any) => (
                        <HStack ref={prov.innerRef} {...prov.draggableProps} {...prov.dragHandleProps} p={2} borderWidth={1} borderRadius={6} justifyContent="space-between">
                          <Box>
                            <Input value={it.name} onChange={(e)=> setItems(prev=> prev.map(x=> x.item_id===it.item_id?{...x,name:e.target.value}:x))} onBlur={(e)=> editItem(it.item_id, { name: e.target.value })} />
                            <div style={{fontSize:12}}>
                              <Textarea value={it.description||''} onChange={(e)=> setItems(prev=> prev.map(x=> x.item_id===it.item_id?{...x,description:e.target.value}:x))} onBlur={(e)=> editItem(it.item_id, { description: e.target.value })} />
                            </div>
                          </Box>
                          <VStack>
                            <HStack>
                              <Button size="sm" onClick={()=>moveItem(it.item_id, -1)}>▲</Button>
                              <Button size="sm" onClick={()=>moveItem(it.item_id, +1)}>▼</Button>
                            </HStack>
                            <HStack>
                              <Button size="sm" colorScheme="red" onClick={()=>removeItem(it.item_id)}>Delete</Button>
                            </HStack>
                            <Box>{it.price} {it.currency}</Box>
                          </VStack>
                        </HStack>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </VStack>
              )}
            </Droppable>

            {/* One column per category, matching the order in `categories` */}
            {categories.map((c) => (
              <Droppable key={c.category_id} droppableId={`cat-${c.category_id}`} type="ITEM">
                {(provided: any) => (
                  <VStack ref={provided.innerRef} {...provided.droppableProps} align="stretch" w="300px" spacing={2}>
                    <Heading size="sm">{c.name}</Heading>
                    {items.filter(it => it.category === c.category_id).map((it, index) => (
                      <Draggable key={it.item_id} draggableId={`item-${it.item_id}`} index={index}>
                        {(prov: any) => (
                          <HStack ref={prov.innerRef} {...prov.draggableProps} {...prov.dragHandleProps} p={2} borderWidth={1} borderRadius={6} justifyContent="space-between">
                            <Box>
                              <Input value={it.name} onChange={(e)=> setItems(prev=> prev.map(x=> x.item_id===it.item_id?{...x,name:e.target.value}:x))} onBlur={(e)=> editItem(it.item_id, { name: e.target.value })} />
                              <div style={{fontSize:12}}>
                                <Textarea value={it.description||''} onChange={(e)=> setItems(prev=> prev.map(x=> x.item_id===it.item_id?{...x,description:e.target.value}:x))} onBlur={(e)=> editItem(it.item_id, { description: e.target.value })} />
                              </div>
                            </Box>
                            <VStack>
                              <HStack>
                                <Button size="sm" onClick={()=>moveItem(it.item_id, -1)}>▲</Button>
                                <Button size="sm" onClick={()=>moveItem(it.item_id, +1)}>▼</Button>
                              </HStack>
                              <HStack>
                                <Button size="sm" colorScheme="red" onClick={()=>removeItem(it.item_id)}>Delete</Button>
                              </HStack>
                              <Box>{it.price} {it.currency}</Box>
                            </VStack>
                          </HStack>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </VStack>
                )}
              </Droppable>
            ))}
          </HStack>
        </DragDropContext>
      </VStack>

      <Button colorScheme="blue" onClick={save} isLoading={loading}>Save Menu</Button>
      <Button ml={2} onClick={()=>window.location.href='/menus'}>Cancel</Button>
    </Box>
  );
}
Sat Aug 30 13:58:22 UTC 2025
