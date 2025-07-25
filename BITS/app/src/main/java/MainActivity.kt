package com.bits.triggerapp

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import org.json.JSONObject
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.io.InputStream
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

class MainActivity : AppCompatActivity() {
    private val CHANNEL_ID = "trigger_channel"
    private val NOTIFICATION_ID = 1

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        createNotificationChannel()

        val btnRunTrigger = findViewById<Button>(R.id.btnRunTrigger)
        val tvResult = findViewById<TextView>(R.id.tvResult)

        btnRunTrigger.setOnClickListener {
            val result = runTriggerDetection()
            if (result.first) {
                tvResult.text = getString(R.string.trigger_detected)
                showNotification(result.second)
            } else {
                tvResult.text = getString(R.string.no_trigger)
            }
        }
    }

    private fun runTriggerDetection(): Pair<Boolean, Float> {
        // Read trigger_input.json from assets
        val jsonString = assets.open("trigger_input.json").bufferedReader().use { it.readText() }
        val json = JSONObject(jsonString)
        val userAlbum = json.getJSONObject("user_album")
        val captions = userAlbum.getJSONArray("captions")
        val captionsList = mutableListOf<String>()
        for (i in 0 until captions.length()) {
            captionsList.add(captions.getString(i))
        }

        // Preprocess captions as needed for your model
        // For demonstration, assume model expects a fixed-size float array per caption (e.g., embedding)
        // Here, you should implement your actual preprocessing (e.g., GloVe embedding lookup)
        // For now, we'll use a dummy input
        val inputShape = intArrayOf(1, captionsList.size, 100) // Example: [1, num_captions, 100]
        val input = Array(1) { Array(captionsList.size) { FloatArray(100) } } // Dummy zero input

        // Load TFLite model
        val tflite = Interpreter(loadModelFile("glove_trigger_model.tflite"))

        // Prepare output buffer
        val output = Array(1) { FloatArray(2) } // Example: [1, 2] for [probability, label]

        // Run inference
        tflite.run(input, output)

        // Parse output (update this according to your model's output)
        val probability = output[0][0]
        val label = output[0][1].toInt()

        return Pair(label == 1, probability)
    }

    private fun loadModelFile(modelFileName: String): MappedByteBuffer {
        val fileDescriptor = assets.openFd(modelFileName)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }

    private fun showNotification(probability: Float) {
        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("Trigger Detected!")
            .setContentText("Probability: $probability")
            .setPriority(NotificationCompat.PRIORITY_HIGH)

        with(NotificationManagerCompat.from(this)) {
            notify(NOTIFICATION_ID, builder.build())
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Trigger Channel"
            val descriptionText = "Channel for trigger notifications"
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
                description = descriptionText
            }
            val notificationManager: NotificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }
} 