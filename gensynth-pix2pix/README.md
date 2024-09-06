# GENSYNTH: Identity-aware synthesis of plain fingerprints with pix2pix

![](imgs/Appendix_Reconstruction_Examples_HQ.png)
Figure 1: Examples of fingerprint reconstruction from minutiae maps with four our models: aug39k_DL, aug39k_PM, synth50k_DL, synth50k_PM

Click [here](imgs/Appendix_Reconstruction_Examples_HQ.emf) to download the same image in emf format for high-fidelity fingerprint images

## Modified pix2pix network
- The project is built upon the open-source code available at [https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix)
- In order to support a fingerprint-native resolution of 500 ppi and enable training with images of 512x512 pixels, we extended both generator and discriminator networks by one convolutional layer
- For exact modifications in the networks please check the commits: [mod_commit1](https://gitti.cs.uni-magdeburg.de/Andrey/gensynth-pix2pix/-/commit/f37482d925875c1a27269943d707dccbae4073de) and [mod_commit2](https://gitti.cs.uni-magdeburg.de/Andrey/gensynth-pix2pix/-/commit/0c88672e9e68ddafc3314ecdf35cdd505254729e) in the git history
- The README.md file of the official repo with detailed instructions on how to train pix2pix and CycleGAN networks can be found [here](p2p_README.md)

## Preprocessing of training images
- Padding to 512x512 pixels (e.g. with "convert" from ImageMagick or the matlab script)
    ```
    # ImageMagick needs to be installed.
    subprocess.call(['convert', inp_file_path, '-gravity', 'center', '-background', 'white', '-extent', '512x512', out_file_path])
    ```
  For a set of fingerprint images you can apply: [apply_padding.py](gensynth-scripts/apply_padding.py)

- Convert images to the type that is compliant with the minutiae extractor (e.g. MINDTCT or Verifinger)
    ```
    # ImageMagick needs to be installed.
    subprocess.call(['convert', file_path, '-units', 'PixelsPerInch', '-density', '500', file_path_new])
    ```
   For a set of fingerprint images you can apply: [convert_500dpi.py](gensynth-scripts/convert_500dpi.py)

- Extract minutiae using MINDTCT or Verifinger and store minutiae templates in text files. \
    An examlpe for Verifinger: [extract_minutiae.py](gensynth-scripts/extract_minutiae.py)

- Create paired training/test images (reference fingerprint + minutiae map) from fingerprints. \
    An example : [fp_plus_min_map_VF_from_fps.py](gensynth-scripts/fp_plus_min_map_VF_from_fps.py)
    ```
    Usage: python fp_plus_min_map_VF_from_fps.py <input_dir> <output_dir> [method] [downscale]>
        input_dir: this folder should include image files only
        output_dir: created minutiae maps will be stored in this folder
        file_name: name of the file to be processed (default=all files in the input folder)
        is_double_image: creates a double image for pix2pix (default=yes)
        method: monoSquare | graySquare | pointingMinutiae | directedMinutiae | patchSkeleton (default=directedMinutiae)
        downscale: 2 for half size, 4 for quarter size and so on, float values are possible (default=1)
    ```

  Minutiae encoding strategies in a minutiae map
    - Mono Squares
        - Each minutiae is represented by a black square of a fixed size with a center at the minutiae location (x,y)
        - The square color is 0
        - The background color is 255

    - Gray Squares
        - Each minutiae is represented by a gray square of a fixed size with a center at (x,y)
        - The shade of gray encodes the minutiae angle 
        - Colors from 0 to 127 quantize the direction of endings
        - Colors from 129 to 255 quantize the direction of bifurcations
        - The background color is 128
        - For 500 ppi fingerprints depicted on 512x512 pixel images, the square size is 13x13 pixels

    - Directed Lines (DL)
        - Each minutiae is represented by a line which starts at (x,y) and is drawn to the direction given by the minutiae angle.
        - The background color is 128
        - For bifurcations, the line color is 255
        - For endings, the line color is 0
        - For 500 ppi fingerprints depicted on 512x512 pixel images, the default line length and width are 14 and 3 pixels correspondingly

    - Pointing Minutiae (PM)
        - The pointing minutiae is a combination of a directed line and a mono square
        - The square color is the same as the line color and depends on the minutiae type
        - For 500 ppi fingerprints depicted on 512x512 pixel images, the default line length and width are 14 and 3 pixels correspondingly, and the default square size is 6






## Model training
Apply paired images for model training by running the train script:\
    ```
    python train.py --dataroot ./datasets/JOURNAL/aug_CM_DL_39k_filtered --name aug_CM_DL_39k_filtered_v2 --model pix2pix --direction BtoA --input_nc 1 --output_nc 1 --netG unet_512 --netD n_layers --n_layers_D 4 --batch_size 64 --no_dropout --preprocess none --checkpoints_dir ./checkpoints/JOURNAL --norm instance --lr 0.002 --n_epochs 60 --n_epochs_decay 60 --save_epoch_freq 5 --save_latest_freq 153600 --display_freq 6400 --print_freq 6400 --num_threads 0 --wandb_project_name JOURNAL --use_wandb
    ```

### Training hyper-parameters
Essential training parameters:
- -- dataroot: Should contain the dataset in pairs of `train,val,test` directories
- -- norm: Available are `batch` and `instance` normalization. In our research we found out that `instance` norm worked well for us. We think, the reason could be that, the fingerprints do not vary much in `statistics`
- -- batch size: Depends on the available `GPU-size`, default size is set to 1
- -- n_epochs: Number of epochs that will be trained with constant learning rate
- -- n_epochs_decay: Number of epochs to linearly decrease the learning rate to zero 
- -- number epochs: Total number of epochs are sum of `n_epochs` and `n_epochs_decay`
- -- lr: Initial learning rate
- -- visualization: Training progress can be seen live in one of the following options
    - Install `visdom-server` and navigate to [http://localhost:8097/](http://localhost:8097/) in local system
    - Also, it can be checked visually in [wandb](https://wandb.ai/) tool. For this, one should create an account in the respected tool and obtain an API key
- Apart from these instructions, for more details, see training [instructions/tips](docs/tips.md)


### Trained models
After accepting the [license agreement](https://omen.cs.uni-magdeburg.de/disclaimer_gensynth_models/index.php) you will receive the password for the [owncloud folder](https://millburn.cs.uni-magdeburg.de/owncloud/index.php/s/mEYrjyLAe8FRHPq) where you can download the best pre-trained models mentioned in the VISAPP 2023 paper:

- **aug39k_PM** : aug39k training dataset, pointing minutiae encoding, instance normalization, 15 epochs
- **aug39k_DL** : aug39k training dataset, directed line encoding, instance normalization, 15 epochs
- **synth50k_PM** : synth50k training dataset, pointing minutiae encoding, instance normalization, 15 epochs
- **synth50k_DL** : synth50k training dataset, directed line encoding, instance normalization, 15 epochs

as well as the model which produces the most visually appealing fingerprint patterns:
- **aug39k_DL_v1** : aug39k training dataset, directed line encoding, batch normalization, 60 epochs + 60 epochs decay


## Single fingerprint generation
- Create a pseudo-random fingerprint, one such can be created by using [Anguli](https://dsl.cds.iisc.ac.in/projects/Anguli/).
- Extract minutiae using MINDTCT or Verifinger and store minutiae templates in text files. \
    An examlpe for Verifinger: [extract_minutiae.py](gensynth-scripts/extract_minutiae.py)
- Apply [minutiae_map_from_minutiae_list.py](gensynth-scripts/minutiae_map_from_minutiae_list.py) script to create a minutiae map from a single fingerprint.
```
Usage: python minutiae_map_from_minutiae_list.py <minutiae_dir> <output_dir> <file_name> [method] [downscale]>
        minutiae_dir: this folder should include minutiae txt files
        output_dir: created minutiae maps will be stored in this folder
        file_name: name of the file to be processed (default=all files in the input folder)
        method: monoSquare | graySquare | pointingMinutiae | directedMinutiae | patchSkeleton (default=pointingMinutiae)
        downscale: 2 for half size, 4 for quarter size and so on, float values are possible (default=1)
```
- Apply the generator part of the model to synthesize fingerprints by running the [test.py](test.py) script with a given minutiae map file (the single minutiae map file should be inside a folder)
```
python test.py --dataroot /path/to/minutiae_maps/ --name aug_CM_DL_39k_filtered_v2 --model test --dataset_mode single --direction AtoB  --input_nc 1 --output_nc 1 --netG unet_512 --netD n_layers --n_layers_D 4 --batch_size 2 --no_dropout --preprocess none --checkpoints_dir /path/to/model --results_dir /path/to/results/ --gpu_ids -1 --norm instance --eval
```

## Fingerprint dataset generation
- Create N pseudo-random minutiae templates, N is the number of fingers. It involves two steps:
    - First generate N fingerprints using [Anguli](https://dsl.cds.iisc.ac.in/projects/Anguli/).
    - Second extract the minutiae from the fingerprints and store them in text files. This process has been explained in `section - Preprocessing of training images`.
- Check that the distribution of basic patterns is realistic (e.g. 60% loops, 25% whorls, 10% arches, 5% tented arches)
- Apply mated_generation.m script with K parameter to augment minutiae templates by K mated samples
- Apply [minutiae_map_from_minutiae_list.py](gensynth-scripts/minutiae_map_from_minutiae_list.py) script to all resulting minutiae templates
- Apply the generator part of the model to synthesize fingerprints by running the [test.py](test.py) script with a given list of minutiae map files.
```
python test.py --dataroot /path/to/minutiae_maps/ --name aug_CM_DL_39k_filtered_v2 --model test --dataset_mode single --direction AtoB  --input_nc 1 --output_nc 1 --netG unet_512 --netD n_layers --n_layers_D 4 --batch_size 2 --no_dropout --preprocess none --checkpoints_dir /path/to/model --results_dir /path/to/results/ --gpu_ids -1 --norm instance --eval
```

After accepting the [license agreement](https://omen.cs.uni-magdeburg.de/disclaimer_gensynth_datasets/index.php) you will receive the password for the [owncloud folder](https://millburn.cs.uni-magdeburg.de/owncloud/index.php/s/j9HnrpX5iaKQjes) where you can download our synthetic fingerprint datasets:

- **AMSL SynFP P2P v1** : 40000 fingerprints of 500 virtual subjects, 8 fingers each (thumb is excluded), 10 impressions per finger, generated using the aforementioned **aug39k_DL_v1** model
- **AMSL SynFP P2P v2** : 40000 fingerprints of 500 virtual subjects, 8 fingers each (thumb is excluded), 10 impressions per finger, generated using the aforementioned **aug39k_PM** model

## Citation
If you find this repo useful for your research, please consider citing this paper:

```
@inproceedings{Makrushin23b,
  author    = {Andrey Makrushin and Venkata Srinath Mannam and Jana Dittmann},
  title     = {Data-Driven Fingerprint Reconstruction from Minutiae Based on Real and Synthetic Training Data},
  booktitle = {Proceedings of the 18th International Joint Conference on Computer Vision, Imaging and Computer Graphics Theory and Applications - Volume 4: VISAPP},
  pages     = {229-237},
  publisher = {{SCITEPRESS}},
  year      = {2023},
  isbn      = {978-989-758-634-7},
  issn      = {2184-4321}
}
```

## License
The project is licensed und the 2-Clause BSD [License](LICENSE)
