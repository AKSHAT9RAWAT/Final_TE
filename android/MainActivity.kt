package com.example.triggerengine

import android.app.Activity
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Bundle
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

class MainActivity : Activity() {

    private lateinit var tflite: Interpreter
    private lateinit var imageView: ImageView
    private lateinit var resultView: TextView
    private val SELECT_IMAGE = 1

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tflite = Interpreter(loadModelFile())
        imageView = findViewById(R.id.image_view)
        resultView = findViewById(R.id.result_view)
        val selectButton = findViewById<Button>(R.id.select_button)

        selectButton.setOnClickListener {
            val intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.type = "image/*"
            startActivityForResult(intent, SELECT_IMAGE)
        }
    }

    private fun loadModelFile(): MappedByteBuffer {
        val fileDescriptor = assets.openFd("glove_trigger_model.tflite")
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }

    private fun runInference(bitmap: Bitmap): FloatArray {
        val input = preprocessBitmap(bitmap)
        val output = FloatArray(1) // Adjust as per your model
        tflite.run(input, output)
        return output
    }

    private fun preprocessBitmap(bitmap: Bitmap): Array<Array<Array<FloatArray>>> {
        val resized = Bitmap.createScaledBitmap(bitmap, 224, 224, true)
        val input = Array(1) { Array(224) { Array(224) { FloatArray(3) } } }
        for (y in 0 until 224) {
            for (x in 0 until 224) {
                val pixel = resized.getPixel(x, y)
                input[0][y][x][0] = ((pixel shr 16 and 0xFF) / 255.0f)
                input[0][y][x][1] = ((pixel shr 8 and 0xFF) / 255.0f)
                input[0][y][x][2] = ((pixel and 0xFF) / 255.0f)
            }
        }
        return input
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == SELECT_IMAGE && resultCode == RESULT_OK && data != null) {
            val uri = data.data
            val inputStream = contentResolver.openInputStream(uri!!)
            val bitmap = BitmapFactory.decodeStream(inputStream)
            imageView.setImageBitmap(bitmap)
            val output = runInference(bitmap)
            resultView.text = "Result: ${output[0]}" // Map this to story/not story as needed
        }
    }
} 