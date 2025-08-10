import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Modal, TextInput, Alert } from 'react-native';
import ConfigService from '../services/ConfigService';
import DeviceActivationService from '../services/DeviceActivationService';

type Props = {
	onActivated: () => void;
};

export default function ActivationScreen({ onActivated }: Props) {
	const [activationCode, setActivationCode] = useState<string>('');
	const [expiresIn, setExpiresIn] = useState<number | null>(null);
	const [qrB64, setQrB64] = useState<string | null>(null);
	const [loading, setLoading] = useState<boolean>(false);
	const stopPollingRef = useRef<null | (() => void)>(null);
	const [showBaseModal, setShowBaseModal] = useState(false);
	const [baseUrl, setBaseUrl] = useState('');

	const requestCode = async () => {
		setLoading(true);
		try {
			await DeviceActivationService.initialize();
			const resp: any = await DeviceActivationService.requestActivationCode();
			setActivationCode(resp.activation_code);
			setExpiresIn(resp.expires_in_seconds ?? 900);
			setQrB64(resp.activation_qr_png_base64 || null);
			// start polling
			if (stopPollingRef.current) stopPollingRef.current();
			stopPollingRef.current = DeviceActivationService.startPollingActivation(
				() => {
					if (stopPollingRef.current) stopPollingRef.current();
					onActivated();
				},
				() => {}
			);
		} catch (e) {
			// noop; UI shows button to retry
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		requestCode();
		return () => {
			if (stopPollingRef.current) stopPollingRef.current();
		};
	}, []);

	useEffect(() => {
		if (expiresIn == null) return;
		if (expiresIn <= 0) return;
		const t = setInterval(() => setExpiresIn((v) => (v ? v - 1 : v)), 1000);
		return () => clearInterval(t);
	}, [expiresIn]);

	return (
		<View style={styles.container}>
			<Text style={styles.title}>Activate This Display</Text>
			<Text style={styles.subtitle}>Use the mobile app to scan the QR or enter the code</Text>
			{qrB64 ? (
				<Image
					source={{ uri: `data:image/png;base64,${qrB64}` }}
					style={styles.qr}
					resizeMode="contain"
				/>
			) : (
				<View style={styles.qrPlaceholder} />
			)}
			<Text style={styles.codeLabel}>Activation Code</Text>
			<Text style={styles.code}>{activationCode || '------'}</Text>
			<Text style={styles.expiry}>
				{expiresIn ? `Expires in ${Math.floor(expiresIn / 60)}m ${expiresIn % 60}s` : 'Generating...'}
			</Text>
			<TouchableOpacity style={[styles.button, loading && styles.buttonDisabled]} onPress={requestCode} disabled={loading}>
				<Text style={styles.buttonText}>{loading ? 'Requesting…' : 'Get New Code'}</Text>
			</TouchableOpacity>
			<TouchableOpacity style={[styles.linkButton]} onPress={async () => {
					const current = await ConfigService.getApiBase();
					setBaseUrl(current);
					setShowBaseModal(true);
				}}>
					<Text style={styles.linkText}>Change Server URL</Text>
				</TouchableOpacity>

				<Modal visible={showBaseModal} transparent animationType="fade" onRequestClose={() => setShowBaseModal(false)}>
					<View style={styles.modalBackdrop}>
						<View style={styles.modalCard}>
							<Text style={styles.modalTitle}>Server Base URL</Text>
							<TextInput value={baseUrl} onChangeText={setBaseUrl} placeholder="http://<ip>:8000/api/v1" style={styles.input} />
							<View style={{ flexDirection: 'row', justifyContent: 'flex-end', marginTop: 12 }}>
								<TouchableOpacity style={[styles.smallBtn, { marginRight: 8 }]} onPress={() => setShowBaseModal(false)}>
									<Text>Cancel</Text>
								</TouchableOpacity>
								<TouchableOpacity style={[styles.smallBtn, { backgroundColor: '#ff8a3d' }]} onPress={async () => {
									try {
										await ConfigService.setApiBase(baseUrl);
										setShowBaseModal(false);
										Alert.alert('Saved', 'Server URL updated. New activations will use this.');
									} catch (e) {
										Alert.alert('Error', 'Could not save URL');
									}
								}}>
									<Text style={{ color: '#000', fontWeight: '700' }}>Save</Text>
								</TouchableOpacity>
							</View>
						</View>
					</View>
				</Modal>
		</View>
	);
}

const styles = StyleSheet.create({
	container: { flex: 1, backgroundColor: '#000', alignItems: 'center', justifyContent: 'center', padding: 24 },
	title: { color: '#fff', fontSize: 36, fontWeight: '700', marginBottom: 8, textAlign: 'center' },
	subtitle: { color: '#ccc', fontSize: 18, marginBottom: 24, textAlign: 'center' },
	qr: { width: 300, height: 300, backgroundColor: '#111', borderRadius: 12, marginBottom: 16 },
	qrPlaceholder: { width: 300, height: 300, backgroundColor: '#111', borderRadius: 12, marginBottom: 16 },
	codeLabel: { color: '#aaa', fontSize: 16, marginTop: 4 },
	code: { color: '#fff', fontSize: 48, letterSpacing: 8, fontWeight: '800', marginVertical: 8 },
	expiry: { color: '#bbb', fontSize: 16, marginBottom: 24 },
	button: { backgroundColor: '#ff8a3d', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
	buttonDisabled: { opacity: 0.6 },
	buttonText: { color: '#000', fontSize: 18, fontWeight: '700' },
	linkButton: { marginTop: 12 },
	linkText: { color: '#8ab4ff', fontSize: 14 },
	modalBackdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.6)', alignItems: 'center', justifyContent: 'center' },
	modalCard: { backgroundColor: '#fff', padding: 16, borderRadius: 8, width: 400 },
	modalTitle: { fontSize: 18, fontWeight: '700', marginBottom: 8 },
	input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 6, padding: 8 },
	smallBtn: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 6, backgroundColor: '#eee' },
});

