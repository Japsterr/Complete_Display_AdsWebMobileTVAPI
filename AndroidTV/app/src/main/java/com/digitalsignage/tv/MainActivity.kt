package com.digitalsignage.tv

import android.content.Intent
import android.os.Bundle
import android.view.KeyEvent
import android.view.View
import android.view.WindowManager
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider

class MainActivity : AppCompatActivity() {
    
    private lateinit var webView: WebView
    private lateinit var viewModel: MainViewModel
    private var isKioskMode = true
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Enable fullscreen and keep screen on
        setupFullscreen()
        
        setContentView(R.layout.activity_main)
        
        viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        
        setupWebView()
        loadTVSimulator()
        
        // Start heartbeat service
        startService(Intent(this, HeartbeatService::class.java))
    }
    
    private fun setupFullscreen() {
        // Keep screen on
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        
        // Hide system UI for kiosk mode
        if (isKioskMode) {
            window.decorView.systemUiVisibility = (
                View.SYSTEM_UI_FLAG_FULLSCREEN
                or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            )
        }
    }
    
    private fun setupWebView() {
        webView = findViewById(R.id.webview)
        
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                // Inject device information
                injectDeviceInfo()
            }
            
            override fun onReceivedError(view: WebView?, errorCode: Int, description: String?, failingUrl: String?) {
                super.onReceivedError(view, errorCode, description, failingUrl)
                showError("Network Error: $description")
            }
        }
        
        val webSettings = webView.settings
        webSettings.javaScriptEnabled = true
        webSettings.domStorageEnabled = true
        webSettings.cacheMode = WebSettings.LOAD_DEFAULT
        webSettings.allowFileAccess = true
        webSettings.allowContentAccess = true
        webSettings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        
        // Enable remote debugging in debug builds
        if (BuildConfig.DEBUG) {
            WebView.setWebContentsDebuggingEnabled(true)
        }
    }
    
    private fun loadTVSimulator() {
        val serverUrl = viewModel.getServerUrl()
        val htmlContent = loadTVSimulatorHTML(serverUrl)
        
        // Load HTML from assets with proper base URL
        webView.loadDataWithBaseURL(
            serverUrl,
            htmlContent,
            "text/html",
            "UTF-8",
            null
        )
    }
    
    private fun loadTVSimulatorHTML(serverUrl: String): String {
        return try {
            val inputStream = assets.open("tv-simulator.html")
            val html = inputStream.bufferedReader().use { it.readText() }
            
            // Replace API_BASE with actual server URL
            html.replace("http://127.0.0.1:8000/api/v1", "$serverUrl/api/v1")
                .replace("TEST-TV-001", viewModel.getDeviceId())
        } catch (e: Exception) {
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Digital Signage TV</title>
                <style>
                    body { 
                        background: #000; 
                        color: #fff; 
                        font-family: Arial; 
                        text-align: center; 
                        padding: 50px; 
                    }
                    .error { color: #ff5252; font-size: 24px; }
                </style>
            </head>
            <body>
                <h1>Digital Signage TV</h1>
                <div class="error">Failed to load TV simulator: ${e.message}</div>
                <p>Device ID: ${viewModel.getDeviceId()}</p>
                <p>Server: $serverUrl</p>
                <p>Please check your network connection and server settings.</p>
            </body>
            </html>
            """.trimIndent()
        }
    }
    
    private fun injectDeviceInfo() {
        val deviceInfo = """
            window.DEVICE_INFO = {
                deviceId: '${viewModel.getDeviceId()}',
                serverUrl: '${viewModel.getServerUrl()}',
                appVersion: '${BuildConfig.VERSION_NAME}',
                androidVersion: '${android.os.Build.VERSION.RELEASE}',
                deviceModel: '${android.os.Build.MODEL}',
                manufacturer: '${android.os.Build.MANUFACTURER}'
            };
            
            // Override device ID if defined in HTML
            if (typeof DEVICE_ID !== 'undefined') {
                window.DEVICE_ID = window.DEVICE_INFO.deviceId;
            }
        """.trimIndent()
        
        webView.evaluateJavascript(deviceInfo, null)
    }
    
    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }
    
    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        // Handle remote control navigation
        when (keyCode) {
            KeyEvent.KEYCODE_MENU, KeyEvent.KEYCODE_SETTINGS -> {
                if (!isKioskMode) {
                    openSettings()
                    return true
                }
            }
            KeyEvent.KEYCODE_BACK -> {
                if (isKioskMode) {
                    // In kiosk mode, don't allow back navigation
                    return true
                }
            }
            // Secret key combo to exit kiosk mode (for debugging)
            KeyEvent.KEYCODE_VOLUME_UP -> {
                if (event?.isShiftPressed == true && event.isCtrlPressed) {
                    isKioskMode = false
                    recreate() // Restart activity without kiosk mode
                    return true
                }
            }
        }
        
        return super.onKeyDown(keyCode, event)
    }
    
    private fun openSettings() {
        val intent = Intent(this, SettingsActivity::class.java)
        startActivity(intent)
    }
    
    override fun onResume() {
        super.onResume()
        setupFullscreen() // Reapply fullscreen after returning from other activities
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Clean up WebView
        webView.destroy()
    }
}
