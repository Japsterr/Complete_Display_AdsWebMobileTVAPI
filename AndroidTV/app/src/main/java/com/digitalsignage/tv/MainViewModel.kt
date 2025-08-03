package com.digitalsignage.tv

import android.content.Context
import android.content.SharedPreferences
import androidx.lifecycle.ViewModel
import java.util.*

class MainViewModel : ViewModel() {
    
    private lateinit var sharedPrefs: SharedPreferences
    
    fun init(context: Context) {
        sharedPrefs = context.getSharedPreferences("DigitalSignageTV", Context.MODE_PRIVATE)
    }
    
    fun getDeviceId(): String {
        return sharedPrefs.getString("device_id", null) ?: generateNewDeviceId()
    }
    
    private fun generateNewDeviceId(): String {
        val deviceId = "TV-${UUID.randomUUID().toString().substring(0, 8).uppercase()}"
        sharedPrefs.edit().putString("device_id", deviceId).apply()
        return deviceId
    }
    
    fun getServerUrl(): String {
        return sharedPrefs.getString("server_url", "http://127.0.0.1:8000") ?: "http://127.0.0.1:8000"
    }
    
    fun setServerUrl(url: String) {
        sharedPrefs.edit().putString("server_url", url).apply()
    }
    
    fun getActivationCode(): String? {
        return sharedPrefs.getString("activation_code", null)
    }
    
    fun setActivationCode(code: String) {
        sharedPrefs.edit().putString("activation_code", code).apply()
    }
    
    fun isActivated(): Boolean {
        return sharedPrefs.getBoolean("is_activated", false)
    }
    
    fun setActivated(activated: Boolean) {
        sharedPrefs.edit().putBoolean("is_activated", activated).apply()
    }
    
    fun getRefreshInterval(): Long {
        return sharedPrefs.getLong("refresh_interval", 30000) // 30 seconds default
    }
    
    fun setRefreshInterval(interval: Long) {
        sharedPrefs.edit().putLong("refresh_interval", interval).apply()
    }
    
    fun clearAllData() {
        sharedPrefs.edit().clear().apply()
    }
}
