import React, {useEffect, useMemo, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import Video from 'react-native-video';
import CampaignService, {Campaign, MediaItem} from '../services/CampaignService';
import AnalyticsService from '../services/AnalyticsService';
import { HEARTBEAT_INTERVAL_MS } from '../config';

const getDims = () => Dimensions.get('window');
let {width: screenWidth, height: screenHeight} = getDims();

const PlayerScreen: React.FC = () => {
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [currentMediaIndex, setCurrentMediaIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadCampaign();

    // start heartbeat
    const hb = setInterval(() => {
      AnalyticsService.sendHeartbeat();
    }, HEARTBEAT_INTERVAL_MS);
    
    // Start polling for campaign updates
  const stopPolling = CampaignService.startPollingCampaign(
      (updatedCampaign) => {
        setCampaign(updatedCampaign);
        if (updatedCampaign && updatedCampaign.media_items.length > 0) {
          setCurrentMediaIndex(0); // Reset to first item when campaign updates
        }
      },
      (error) => {
        console.error('Campaign polling error:', error);
        setError(`Campaign update error: ${error.message}`);
      }
    );

  return () => { clearInterval(hb); stopPolling(); };
  }, []);

  // Track orientation changes
  useEffect(() => {
    const sub = Dimensions.addEventListener('change', ({window}) => {
      screenWidth = window.width; // update module vars
      screenHeight = window.height;
      // trigger rerender
      setDimsVersion(v => v + 1);
    });
    return () => {
      // RN >= 0.65 returns subscription with remove(); in newer versions, removeEventListener is deprecated
      // @ts-ignore
      sub?.remove?.();
    };
  }, []);

  const [dimsVersion, setDimsVersion] = useState(0);

  // Auto-advance through media items (images use timer; videos advance on onEnd)
  useEffect(() => {
    if (!campaign || campaign.media_items.length === 0) return;

    const currentMedia = campaign.media_items[currentMediaIndex];
    if (currentMedia.media_type === 'video') {
      // For video, rely on onEnd to advance
      return;
    }
    const duration = currentMedia.duration * 1000; // Convert to ms
    const timer = setTimeout(() => {
      try {
        AnalyticsService.recordImpression({
          device_id: '',
          media_id: currentMedia.media_id,
          campaign_id: campaign.campaign_id,
          duration_shown: currentMedia.duration,
          scheduled_duration: currentMedia.duration,
          completed: true,
          sequence_number: currentMediaIndex + 1,
          total_media_in_campaign: campaign.media_items.length,
        });
      } catch {}
      setCurrentMediaIndex((prevIndex) => (prevIndex + 1) % campaign.media_items.length);
    }, duration);
    return () => clearTimeout(timer);
  }, [campaign, currentMediaIndex]);

  const loadCampaign = async () => {
    try {
      setLoading(true);
      setError('');
      
      const campaignData = await CampaignService.getCurrentCampaign();
      setCampaign(campaignData);
      
      if (campaignData && campaignData.media_items.length > 0) {
        setCurrentMediaIndex(0);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to load campaign:', error);
      setError(error instanceof Error ? error.message : 'Failed to load campaign');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#FFFFFF" />
        <Text style={styles.loadingText}>Loading campaign...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Campaign Error</Text>
          <Text style={styles.errorMessage}>{error}</Text>
          <Text style={styles.retryText}>Retrying automatically...</Text>
        </View>
      </View>
    );
  }

  if (!campaign || campaign.media_items.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.noCampaignContainer}>
          <Text style={styles.noCampaignTitle}>No Campaign Assigned</Text>
          <Text style={styles.noCampaignMessage}>
            This display is activated but no campaign has been assigned yet.
          </Text>
          <Text style={styles.noCampaignInstructions}>
            Please assign a campaign to this display in the web dashboard.
          </Text>
        </View>
      </View>
    );
  }

  const currentMedia = campaign.media_items[currentMediaIndex];
  const [mediaUrl, setMediaUrl] = useState<string>('');

  useEffect(() => {
    (async () => {
      if (!currentMedia) return;
      const u = await CampaignService.getMediaUrlAsync(currentMedia);
      setMediaUrl(u);
    })();
  }, [currentMedia]);

  const normalize = campaign?.normalize_to_orientation || 'none';
  const wrapperStyle = useMemo(() => {
    const isLandscapeDevice = screenWidth >= screenHeight;
    if (normalize === 'portrait' && isLandscapeDevice) {
      return [styles.wrapper, { width: screenHeight, height: screenWidth, transform: [{ rotate: '90deg' }] }];
    }
    if (normalize === 'landscape' && !isLandscapeDevice) {
      return [styles.wrapper, { width: screenHeight, height: screenWidth, transform: [{ rotate: '-90deg' }] }];
    }
    return [styles.wrapper, { width: screenWidth, height: screenHeight }];
  }, [normalize, dimsVersion]);

  return (
    <View style={styles.container}>
      <View style={wrapperStyle as any}>
        {currentMedia.media_type === 'image' ? (
          <Image
            source={{uri: mediaUrl}}
            style={styles.mediaInner}
            resizeMode="contain"
          />
        ) : (
          <Video
            source={{uri: mediaUrl}}
            style={styles.mediaInner}
            resizeMode="contain"
            paused={false}
            onEnd={() => {
            try {
              AnalyticsService.recordImpression({
                device_id: '',
                media_id: currentMedia.media_id,
                campaign_id: campaign.campaign_id,
                duration_shown: currentMedia.duration,
                scheduled_duration: currentMedia.duration,
                completed: true,
                sequence_number: currentMediaIndex + 1,
                total_media_in_campaign: campaign.media_items.length,
              });
            } catch {}
            setCurrentMediaIndex((prevIndex) => (prevIndex + 1) % campaign.media_items.length);
            }}
            onError={(e: any) => setError(`Video error: ${JSON.stringify((e && (e.nativeEvent || e)) || {})}`)}
          />
        )}
      </View>
      
      {/* Campaign info overlay (can be hidden in production) */}
      <View style={styles.infoOverlay}>
        <Text style={styles.campaignInfo}>
          {campaign.name} • {currentMediaIndex + 1}/{campaign.media_items.length}
        </Text>
        <Text style={styles.mediaInfo}>
          {currentMedia.name} ({currentMedia.duration}s)
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  wrapper: {
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  mediaInner: {
    width: '100%',
    height: '100%',
  },
  videoPlaceholder: {
    width: screenWidth,
    height: screenHeight,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
  },
  videoPlaceholderText: {
    color: '#FFFFFF',
    fontSize: 32,
    fontWeight: '300',
    textAlign: 'center',
  },
  loadingText: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: '300',
    marginTop: 20,
    textAlign: 'center',
  },
  errorContainer: {
    alignItems: 'center',
    maxWidth: 600,
    padding: 40,
  },
  errorTitle: {
    color: '#FF5252',
    fontSize: 36,
    fontWeight: '600',
    marginBottom: 20,
    textAlign: 'center',
  },
  errorMessage: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: '400',
    marginBottom: 20,
    textAlign: 'center',
    lineHeight: 32,
  },
  retryText: {
    color: '#CCCCCC',
    fontSize: 20,
    fontWeight: '300',
    textAlign: 'center',
    lineHeight: 28,
  },
  noCampaignContainer: {
    alignItems: 'center',
    maxWidth: 800,
    padding: 40,
  },
  noCampaignTitle: {
    color: '#FFFFFF',
    fontSize: 48,
    fontWeight: '600',
    marginBottom: 30,
    textAlign: 'center',
  },
  noCampaignMessage: {
    color: '#CCCCCC',
    fontSize: 28,
    fontWeight: '400',
    marginBottom: 20,
    textAlign: 'center',
    lineHeight: 36,
  },
  noCampaignInstructions: {
    color: '#CCCCCC',
    fontSize: 24,
    fontWeight: '300',
    textAlign: 'center',
    lineHeight: 32,
  },
  infoOverlay: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: 15,
    borderRadius: 8,
  },
  campaignInfo: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 5,
  },
  mediaInfo: {
    color: '#CCCCCC',
    fontSize: 14,
    fontWeight: '400',
  },
});

export default PlayerScreen;
