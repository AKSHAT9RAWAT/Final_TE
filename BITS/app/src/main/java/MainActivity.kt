////package com.bits.triggerapp
////
////import android.app.NotificationChannel
////import android.app.NotificationManager
////import android.content.Context
////import android.os.Build
////import android.os.Bundle
////import android.widget.Button
////import android.widget.TextView
////import androidx.appcompat.app.AppCompatActivity
////import androidx.core.app.NotificationCompat
////import androidx.core.app.NotificationManagerCompat
////import org.json.JSONObject
////import org.tensorflow.lite.Interpreter
////import java.io.BufferedReader
////import java.io.FileInputStream
////import java.io.InputStreamReader
////import java.nio.MappedByteBuffer
////import java.nio.channels.FileChannel
////import android.Manifest
////import android.content.pm.PackageManager
////import androidx.activity.result.contract.ActivityResultContracts
////import androidx.core.content.ContextCompat
////import android.util.Log
////
////
////class MainActivity : AppCompatActivity() {
////    private val CHANNEL_ID = "trigger_channel"
////    private val NOTIFICATION_ID = 1
////    private val GLOVE_FILE = "glove.6B.100d.txt"
////    private val EMBEDDING_DIM = 100
////    private lateinit var word2vec: HashMap<String, FloatArray>
////
////    override fun onCreate(savedInstanceState: Bundle?) {
////        super.onCreate(savedInstanceState)
////        setContentView(R.layout.activity_main)
////
////        createNotificationChannel()
////
////        // Load GloVe vectors once at startup
////        Thread {
////            word2vec = loadGloveFromAssets()
////        }.start()
////
////        val btnRunTrigger = findViewById<Button>(R.id.btnRunTrigger)
////        val tvResult = findViewById<TextView>(R.id.tvResult)
////
////        btnRunTrigger.setOnClickListener {
////            Thread {
////                val result = runTriggerDetection()
////                runOnUiThread {
////                    if (result.first) {
////                        tvResult.text = getString(R.string.trigger_detected)
////                        showNotification(result.second)
////                    } else {
////                        tvResult.text = getString(R.string.no_trigger)
////                    }
////                }
////            }.start()
////        }
////    }
////
////    private fun runTriggerDetection(): Pair<Boolean, Float> {
////        // Read trigger_input.json from assets
////        val jsonString = assets.open("trigger_input.json").bufferedReader().use { it.readText() }
////        val json = JSONObject(jsonString)
////        val userAlbum = json.getJSONObject("user_album")
////        val captions = userAlbum.getJSONArray("captions")
////        val captionsList = mutableListOf<String>()
////        for (i in 0 until captions.length()) {
////            captionsList.add(captions.getString(i))
////        }
////
////        // Compute album embedding using GloVe
////        val embedding = albumToEmbedding(captionsList)
////        val input = Array(1) { embedding } // shape: [1, 100]
////
////        // Load TFLite model
////        val tflite = Interpreter(loadModelFile("glove_trigger_model.tflite"))
////
////        // Prepare output buffer
////        val output = Array(1) { FloatArray(1) } // shape: [1, 1] for sigmoid output
////
////        // Run inference
////        tflite.run(input, output)
////
////        // Parse output
////        val probability = output[0][0]
////        val label = if (probability >= 0.5f) 1 else 0
////
////        return Pair(label == 1, probability)
////    }
////
////    private fun loadGloveFromAssets(): HashMap<String, FloatArray> {
////        val word2vec = HashMap<String, FloatArray>()
////        val inputStream = assets.open(GLOVE_FILE)
////        val reader = BufferedReader(InputStreamReader(inputStream))
////        var line: String?
////        while (reader.readLine().also { line = it } != null) {
////            val values = line!!.split(" ")
////            val word = values[0]
////            val vector = FloatArray(EMBEDDING_DIM) { i -> values[i + 1].toFloat() }
////            word2vec[word] = vector
////        }
////        reader.close()
////        return word2vec
////    }
////
////    private fun sentenceToEmbedding(sentence: String): FloatArray {
////        val words = sentence.lowercase().split(" ")
////        val vectors = words.mapNotNull { word2vec[it] }
////        if (vectors.isEmpty()) return FloatArray(EMBEDDING_DIM) { 0f }
////        val avg = FloatArray(EMBEDDING_DIM) { 0f }
////        for (vec in vectors) {
////            for (i in 0 until EMBEDDING_DIM) {
////                avg[i] += vec[i]
////            }
////        }
////        for (i in 0 until EMBEDDING_DIM) {
////            avg[i] = avg[i]/vectors.size
////        }
////        return avg
////    }
////
////    private fun albumToEmbedding(captions: List<String>): FloatArray {
////        val captionEmbeddings = captions.map { sentenceToEmbedding(it) }
////        val avg = FloatArray(EMBEDDING_DIM) { 0f }
////        for (vec in captionEmbeddings) {
////            for (i in 0 until EMBEDDING_DIM) {
////                avg[i] += vec[i]
////            }
////        }
////        for (i in 0 until EMBEDDING_DIM) {
////            avg[i] =avg[i]/captionEmbeddings.size
////        }
////        return avg
////    }
////
////    private fun loadModelFile(modelFileName: String): MappedByteBuffer {
////        val fileDescriptor = assets.openFd(modelFileName)
////        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
////        val fileChannel = inputStream.channel
////        val startOffset = fileDescriptor.startOffset
////        val declaredLength = fileDescriptor.declaredLength
////        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
////    }
////
////    private fun showNotification(probability: Float) {
////        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
////            .setSmallIcon(android.R.drawable.ic_dialog_info)
////            .setContentTitle("Trigger Detected!")
////            .setContentText("Probability: $probability")
////            .setPriority(NotificationCompat.PRIORITY_HIGH)
////
////        with(NotificationManagerCompat.from(this)) {
////            notify(NOTIFICATION_ID, builder.build())
////        }
////
////    }
////
////    private fun createNotificationChannel() {
////        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
////            val name = "Trigger Channel"
////            val descriptionText = "Channel for trigger notifications"
////            val importance = NotificationManager.IMPORTANCE_HIGH
////            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
////                description = descriptionText
////            }
////            val notificationManager: NotificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
////            notificationManager.createNotificationChannel(channel)
////        }
////    }
////}
//
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
import kotlinx.coroutines.*
import org.json.JSONObject
import org.tensorflow.lite.Interpreter
import java.io.*
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import android.util.Log
import android.Manifest
import androidx.core.app.ActivityCompat
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat

private val EVENT_TAGS = mapOf(
    "birthday" to listOf("birthday", "cake", "candles", "present", "gift", "balloons"),
    "wedding" to listOf("wedding", "bride", "groom", "aisle", "altar", "reception", "vows"),
    "graduation" to listOf("graduation", "gown", "diploma", "cap", "ceremony", "degree"),
    "sports" to listOf("sports", "trophy", "match", "goal", "team", "field", "stadium", "score",
        "football", "soccer", "basketball", "tennis", "cricket", "bat", "ball", "racket", "hoop", "net", "badminton", "hockey", "baseball", "volleyball", "pitch", "umpire", "referee", "athlete", "race"),
    "picnic" to listOf("picnic", "blanket", "basket", "grass", "tree", "sandwich"),
    "festival" to listOf("parade", "festival", "float", "costume", "lantern", "celebration"),
    "travel" to listOf("beach", "mountain", "sunset", "trip", "boat", "vacation"),
    "pets" to listOf("pet", "pets", "dog", "puppy", "cat", "kitten", "rabbit", "bunny", "bird", "parrot", "fish", "goldfish",
        "aquarium", "leash", "fur", "bark", "meow", "chirp", "purring", "playing fetch", "fins", "claws", "whiskers"),
    "parade" to listOf("parade", "march", "balloons", "flags", "crowd", "banner", "music", "drum", "cheer"),
    "swimming" to listOf("swimming", "pool", "swim", "float", "goggles", "diving", "splash", "swimsuit"),
    "seminar_event" to listOf("presentation", "conference", "projector", "screen", "auditorium", "audience", "speaker", "microphone", "stage", "session", "event", "nasa"),
    "lunch" to listOf("lunch", "meal", "food", "dining", "snack", "restaurant", "buffet", "cuisine", "plate", "fork", "spoon", "brunch", "lunchbox", "eating", "kitchen")
)

private val TEMPLATES = mapOf(
    "birthday" to "Someone's birthday bash! Want to create a memory?",
    "wedding" to "A beautiful wedding captured! Shall we build your story?",
    "graduation" to "Graduation day vibes! Ready to celebrate your journey?",
    "sports" to "Game time moments! Let's craft your winning memory!",
    "picnic" to "Picnic memories in the open! Want to share it?",
    "festival" to "Celebrating traditions! Let's make this story special!",
    "travel" to "Travel diaries look exciting! Want to save the journey?",
    "pets" to "Furry, feathery, or fishy friends captured! Want to relive those pet moments?",
    "parade" to "A colorful parade in action! Ready to capture the joy?",
    "swimming" to "Making a splash! Shall we dive into this memory?",
    "seminar_event" to "Professional moments spotted! Shall we turn this session into a story?",
    "lunch" to "Lunchtime vibes! Want to turn this meal into a story?"
)

private val GENERIC_TEMPLATES = listOf(
    "Looks like you've captured something memorable! Want to create a story?",
    "A meaningful memory spotted! Ready to turn it into a post?",
    "Looks important! Want to build a moment around it?"
)

private fun extractTags(caption: String): List<String> {
    val tags = mutableListOf<String>()
    val text = caption.lowercase()
    for ((tag, keywords) in EVENT_TAGS) {
        if (keywords.any { text.contains(it) }) {
            tags.add(tag)
        }
    }
    return tags
}

private fun getTopEventTag(captions: List<String>): String? {
    val tagCounter = mutableMapOf<String, Int>()
    for (caption in captions) {
        for (tag in extractTags(caption)) {
            tagCounter[tag] = tagCounter.getOrDefault(tag, 0) + 1
        }
    }
    return tagCounter.maxByOrNull { it.value }?.key
}

class MainActivity : AppCompatActivity() {
    private val CHANNEL_ID = "trigger_channel"
    private val NOTIFICATION_ID = 1
    private val GLOVE_FILE = "glove.6B.100d.txt"
    private val EMBEDDING_DIM = 100
    private lateinit var word2vec: HashMap<String, FloatArray>

    private lateinit var tvResult: TextView
    private lateinit var btnRunTrigger: Button


    private fun getCaptionsFromJson(): List<String> {
        val jsonString = assets.open("trigger_input.json").bufferedReader().use { it.readText() }
        val json = JSONObject(jsonString)
        val captions = json.getJSONObject("user_album").getJSONArray("captions")
        return List(captions.length()) { i -> captions.getString(i) }
    }


    override fun onCreate(savedInstanceState: Bundle?) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                    1001
                )
            }
        }


        //btnRunTrigger.isEnabled = false // Add this line in onCreate before coroutine starts

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvResult = findViewById(R.id.tvResult)
        btnRunTrigger = findViewById(R.id.btnRunTrigger)

        createNotificationChannel()

        Log.d("DEBUG", "onCreate: Starting GloVe loading process")
        CoroutineScope(Dispatchers.IO).launch {
            Log.d("DEBUG", "onCreate: Collecting needed words from captions")
            val neededWords = getNeededWordsFromCaptions()
            Log.d("DEBUG", "onCreate: Needed words collected: ${'$'}{neededWords.size}")
            word2vec = loadGloveFromAssets(neededWords)
            Log.d("DEBUG", "onCreate: GloVe loaded with ${'$'}{word2vec.size} words")

            withContext(Dispatchers.Main) {
                btnRunTrigger.isEnabled = true
                Log.d("DEBUG", "onCreate: Button enabled")
            }
        }

        btnRunTrigger.setOnClickListener {
            Log.d("DEBUG", "Button clicked: Starting trigger detection")

            // Request permission before continuing
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED
                ) {
                    ActivityCompat.requestPermissions(
                        this,
                        arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                        1001
                    )
                    return@setOnClickListener // Exit and wait for permission result
                }
            }

            CoroutineScope(Dispatchers.IO).launch {
                val result = runTriggerDetection()
                val captions = getCaptionsFromJson() // ✅ Needed for showNotification
                Log.d("DEBUG", "Button clicked: Trigger detection finished")
                withContext(Dispatchers.Main) {
                    if (result.first) {
                        tvResult.text = getString(R.string.trigger_detected)
                        showNotification(result.second, captions)
                    } else {
                        tvResult.text = getString(R.string.no_trigger)
                    }
                }
            }
        }


//        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
//            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
//                != PackageManager.PERMISSION_GRANTED) {
//                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1001)
//            }
//        }
    }

    private fun runTriggerDetection(): Pair<Boolean, Float> {
        Log.d("DEBUG", "runTriggerDetection: Reading trigger_input.json")
        val jsonString = assets.open("trigger_input.json").bufferedReader().use { it.readText() }
        Log.d("DEBUG", "runTriggerDetection: JSON read, parsing captions")
        val json = JSONObject(jsonString)
        val captions = json.getJSONObject("user_album").getJSONArray("captions")

        val captionsList = List(captions.length()) { i -> captions.getString(i) }
        Log.d("DEBUG", "runTriggerDetection: Captions parsed, computing embedding")
        val embedding = albumToEmbedding(captionsList)

        val input = Array(1) { embedding }
        val output = Array(1) { FloatArray(1) }

        Log.d("DEBUG", "runTriggerDetection: Loading TFLite model")
        val tflite = Interpreter(loadModelFile("glove_trigger_model.tflite"))
        Log.d("DEBUG", "runTriggerDetection: Running inference")
        tflite.run(input, output)
        Log.d("DEBUG", "runTriggerDetection: Inference complete")

        val probability = output[0][0]
        val label = if (probability >= 0.5f) 1 else 0
        Log.d("DEBUG", "runTriggerDetection: Probability=${'$'}probability, Label=${'$'}label")

        return Pair(label == 1, probability)
    }
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == 1001) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Log.d("Permission", "Notification permission granted")
                btnRunTrigger.performClick() // ✅ Retry the operation
            } else {
                Log.d("Permission", "Notification permission denied")
                Toast.makeText(this, "Permission required to show notifications.", Toast.LENGTH_SHORT).show()
            }
        }
    }


    private fun getNeededWordsFromCaptions(): Set<String> {
        Log.d("DEBUG", "getNeededWordsFromCaptions: Reading trigger_input.json")
        val jsonString = assets.open("trigger_input.json").bufferedReader().use { it.readText() }
        Log.d("DEBUG", "getNeededWordsFromCaptions: JSON read, parsing captions")
        val json = JSONObject(jsonString)
        val captions = json.getJSONObject("user_album").getJSONArray("captions")
        val neededWords = mutableSetOf<String>()
        for (i in 0 until captions.length()) {
            val words = captions.getString(i).lowercase().split(" ")
            neededWords.addAll(words)
        }
        Log.d("DEBUG", "getNeededWordsFromCaptions: Collected ${'$'}{neededWords.size} unique words")
        return neededWords
    }

    private fun loadGloveFromAssets(neededWords: Set<String>): HashMap<String, FloatArray> {
        Log.d("DEBUG", "loadGloveFromAssets: Loading GloVe vectors from assets")
        val word2vec = HashMap<String, FloatArray>()
        var totalLines = 0
        var matchedLines = 0
        assets.open(GLOVE_FILE).bufferedReader().useLines { lines ->
            lines.forEach { line ->
                totalLines++
                val values = line.split(" ")
                if (values.size == EMBEDDING_DIM + 1) {
                    val word = values[0]
                    if (neededWords.contains(word)) {
                        val vector = FloatArray(EMBEDDING_DIM) { i -> values[i + 1].toFloat() }
                        word2vec[word] = vector
                        matchedLines++
                    }
                }
            }
        }
        Log.d("DEBUG", "loadGloveFromAssets: Loaded ${'$'}matchedLines words out of ${'$'}{neededWords.size} needed, scanned ${'$'}totalLines lines")
        return word2vec
    }

    private fun sentenceToEmbedding(sentence: String): FloatArray {
        val vectors = sentence.lowercase().split(" ").mapNotNull { word2vec[it] }
        if (vectors.isEmpty()) return FloatArray(EMBEDDING_DIM) { 0f }

        val avg = FloatArray(EMBEDDING_DIM)
        for (vec in vectors) {
            for (i in vec.indices) {
                avg[i] += vec[i]
            }
        }
        for (i in avg.indices) {
            avg[i] =avg[i]/ vectors.size
        }
        return avg
    }

    private fun albumToEmbedding(captions: List<String>): FloatArray {
        val captionEmbeddings = captions.map { sentenceToEmbedding(it) }
        val avg = FloatArray(EMBEDDING_DIM)
        for (vec in captionEmbeddings) {
            for (i in vec.indices) {
                avg[i] += vec[i]
            }
        }
        for (i in avg.indices) {
            avg[i] =avg[i]/ captionEmbeddings.size
        }
        return avg
    }

    private fun loadModelFile(modelFileName: String): MappedByteBuffer {
        val fileDescriptor = assets.openFd(modelFileName)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, fileDescriptor.startOffset, fileDescriptor.declaredLength)
    }

    private fun showNotification(probability: Float, captions: List<String>) {
        val topTag = getTopEventTag(captions)
        val message = if (topTag != null) {
            TEMPLATES[topTag] ?: GENERIC_TEMPLATES.random()
        } else {
            GENERIC_TEMPLATES.random()
        }

        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("Trigger Detected!")
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_HIGH)

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED) {
            with(NotificationManagerCompat.from(this)) {
                notify(NOTIFICATION_ID, builder.build())
            }
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
