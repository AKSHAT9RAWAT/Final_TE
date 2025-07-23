# Android App for Trigger Engine

This folder contains the starter files and instructions for building an Android app that uses the TFLite trigger engine to determine if uploaded images tell a meaningful story.

## Structure

- `MainActivity.kt`: Main activity for the app (Kotlin)
- `activity_main.xml`: UI layout
- `glove_trigger_model.tflite`: Place your TFLite model here
- `README.md`: This file

## Instructions

1. Open this folder in Android Studio.
2. Add your `glove_trigger_model.tflite` file to the `assets` directory.
3. Use the provided `MainActivity.kt` and `activity_main.xml` as starting points.
4. Add TensorFlow Lite dependency in your `build.gradle` as described below.

## Dependencies

Add to your `build.gradle`:

```
dependencies {
    implementation 'org.tensorflow:tensorflow-lite:2.14.0'
}
```
