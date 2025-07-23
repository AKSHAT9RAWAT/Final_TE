import tensorflow as tf

saved_model_dir = "glove_trigger_model_tf"

converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
tflite_model = converter.convert()

with open("glove_trigger_model.tflite", "wb") as f:
    f.write(tflite_model)

print("Exported to glove_trigger_model.tflite")