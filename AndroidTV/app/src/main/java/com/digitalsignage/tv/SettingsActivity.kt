package com.digitalsignage.tv

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider

class SettingsActivity : AppCompatActivity() {
    
    private lateinit var viewModel: MainViewModel
    private lateinit var etServerUrl: EditText
    private lateinit var etActivationCode: EditText
    private lateinit var tvDeviceId: TextView
    private lateinit var switchKioskMode: Switch
    private lateinit var seekRefreshInterval: SeekBar
    private lateinit var tvRefreshInterval: TextView
    private lateinit var btnSave: Button
    private lateinit var btnRestart: Button
    private lateinit var btnReset: Button
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)
        
        viewModel = ViewModelProvider(this)[MainViewModel::class.java]
        viewModel.init(this)
        
        setupViews()
        loadCurrentSettings()
        setupListeners()
    }
    
    private fun setupViews() {
        etServerUrl = findViewById(R.id.et_server_url)
        etActivationCode = findViewById(R.id.et_activation_code)
        tvDeviceId = findViewById(R.id.tv_device_id)
        switchKioskMode = findViewById(R.id.switch_kiosk_mode)
        seekRefreshInterval = findViewById(R.id.seek_refresh_interval)
        tvRefreshInterval = findViewById(R.id.tv_refresh_interval)
        btnSave = findViewById(R.id.btn_save)
        btnRestart = findViewById(R.id.btn_restart)
        btnReset = findViewById(R.id.btn_reset)
        
        // Setup SeekBar
        seekRefreshInterval.max = 300 // 5 minutes max
        seekRefreshInterval.progress = 30 // 30 seconds default
        
        seekRefreshInterval.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val seconds = if (progress < 5) 5 else progress // Minimum 5 seconds
                tvRefreshInterval.text = "${seconds}s"
            }
            
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })
    }
    
    private fun loadCurrentSettings() {
        etServerUrl.setText(viewModel.getServerUrl())
        etActivationCode.setText(viewModel.getActivationCode() ?: "")
        tvDeviceId.text = "Device ID: ${viewModel.getDeviceId()}"
        
        val refreshInterval = (viewModel.getRefreshInterval() / 1000).toInt()
        seekRefreshInterval.progress = refreshInterval
        tvRefreshInterval.text = "${refreshInterval}s"
        
        switchKioskMode.isChecked = true // Default to kiosk mode
    }
    
    private fun setupListeners() {
        btnSave.setOnClickListener {
            saveSettings()
        }
        
        btnRestart.setOnClickListener {
            restartApp()
        }
        
        btnReset.setOnClickListener {
            resetSettings()
        }
    }
    
    private fun saveSettings() {
        val serverUrl = etServerUrl.text.toString().trim()
        val activationCode = etActivationCode.text.toString().trim()
        val refreshInterval = (if (seekRefreshInterval.progress < 5) 5 else seekRefreshInterval.progress) * 1000L
        
        if (serverUrl.isEmpty()) {
            Toast.makeText(this, "Server URL cannot be empty", Toast.LENGTH_SHORT).show()
            return
        }
        
        viewModel.setServerUrl(serverUrl)
        if (activationCode.isNotEmpty()) {
            viewModel.setActivationCode(activationCode)
        }
        viewModel.setRefreshInterval(refreshInterval)
        
        Toast.makeText(this, "Settings saved successfully", Toast.LENGTH_SHORT).show()
        
        // Return to main activity
        finish()
    }
    
    private fun restartApp() {
        val intent = Intent(this, MainActivity::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent)
        finish()
    }
    
    private fun resetSettings() {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("Reset Settings")
            .setMessage("This will reset all settings and generate a new device ID. Are you sure?")
            .setPositiveButton("Reset") { _, _ ->
                viewModel.clearAllData()
                Toast.makeText(this, "Settings reset successfully", Toast.LENGTH_SHORT).show()
                restartApp()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
