# Crop image model

The training script builds a 14-class MobileNetV3 classifier for the crop
options in the offline diagnosis screen.

1. Install the training dependencies:

   `pip install -r ml/requirements-training.txt`

2. Create one folder per class under `ml/dataset` using the exact names below:

   `Tomato__Early_blight`, `Tomato__Late_blight`,
   `Tomato__Bacterial_spot`, `Tomato__Leaf_mold`,
   `Rice__Blast`, `Rice__Brown_spot`, `Rice__Bacterial_leaf_blight`,
   `Cotton__Bacterial_blight`, `Cotton__Bollworm_damage`,
   `Chilli__Leaf_curl`, `Chilli__Powdery_mildew`, `Chilli__Thrips_damage`,
   `Groundnut__Tikka_leaf_spot`, `Groundnut__Rust`

3. Put several correctly labelled field images in every folder and train:

   `python ml/train_crop_model.py --data ml/dataset --output ml/artifacts/crop_health.pt`

The current repository does not contain labeled images, so training cannot
produce a valid disease model yet. The generated weights must also be
converted to a mobile format and bundled with the Expo app before offline
image inference can be enabled.
