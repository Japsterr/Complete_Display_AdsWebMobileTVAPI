import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import CampaignService, {Campaign, MediaItem} from '../services/CampaignService';

const {width: screenWidth, height: screenHeight} = Dimensions.get('window');

const PlayerScreen: React.FC = () => {
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [currentMediaIndex, setCurrentMediaIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadCampaign();
    
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

    return () => stopPolling();
  }, []);

  // Auto-advance through media items
  useEffect(() => {
    if (!campaign || campaign.media_items.length === 0) return;

    const currentMedia = campaign.media_items[currentMediaIndex];
    const duration = currentMedia.duration * 1000; // Convert to milliseconds

    const timer = setTimeout(() => {
      setCurrentMediaIndex((prevIndex) => 
        (prevIndex + 1) % campaign.media_items.length
      );
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
  const mediaUrl = CampaignService.getMediaUrl(currentMedia);

  return (
    <View style={styles.container}>
      {currentMedia.media_type === 'image' ? (
        <Image
          source={{uri: mediaUrl}}
          style={styles.media}
          resizeMode="contain"
        />
      ) : (
        // For video, we'll need react-native-video or similar
        // For now, show placeholder
        <View style={styles.videoPlaceholder}>
          <Text style={styles.videoPlaceholderText}>
            Video: {currentMedia.name}
          </Text>
        </View>
      )}
      
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
  media: {
    width: screenWidth,
    height: screenHeight,
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
