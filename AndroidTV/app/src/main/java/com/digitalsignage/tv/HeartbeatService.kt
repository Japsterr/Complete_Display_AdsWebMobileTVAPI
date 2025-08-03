package com.digitalsignage.tv

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

class HeartbeatService : Service() {
    
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val client = OkHttpClient()
    private lateinit var viewModel: MainViewModel
    
    companion object {
        private const val TAG = "HeartbeatService"
        private const val HEARTBEAT_INTERVAL = 30000L // 30 seconds
    }
    
    override fun onCreate() {
        super.onCreate()
        viewModel = MainViewModel()
        viewModel.init(this)
        startHeartbeat()
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    private fun startHeartbeat() {
        serviceScope.launch {
            while (isActive) {
                try {
                    sendHeartbeat()
                    delay(HEARTBEAT_INTERVAL)
                } catch (e: Exception) {
                    Log.e(TAG, "Heartbeat error: ${e.message}")
                    delay(HEARTBEAT_INTERVAL)
                }
            }
        }
    }
    
    private suspend fun sendHeartbeat() {
        val serverUrl = viewModel.getServerUrl()
        val deviceId = viewModel.getDeviceId()
        
        val heartbeatData = JSONObject().apply {
            put("device_id", deviceId)
            put("timestamp", System.currentTimeMillis())
            put("status", "active")
            put("app_version", BuildConfig.VERSION_NAME)
        }
        
        val requestBody = heartbeatData.toString()
            .toRequestBody("application/json; charset=utf-8".toMediaType())
        
        val request = Request.Builder()
            .url("$serverUrl/api/v1/device-heartbeat/")
            .post(requestBody)
            .addHeader("Content-Type", "application/json")
            .build()
        
        withContext(Dispatchers.IO) {
            try {
                client.newCall(request).execute().use { response ->
                    if (response.isSuccessful) {
                        Log.d(TAG, "Heartbeat sent successfully")
                    } else {
                        Log.w(TAG, "Heartbeat failed: ${response.code}")
                    }
                }
            } catch (e: IOException) {
                Log.e(TAG, "Network error sending heartbeat: ${e.message}")
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
    }
}
