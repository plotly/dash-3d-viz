import napari
from nilearn import image
from skimage import segmentation

img = image.image.load_img('assets/BraTS19_2013_10_1_flair.nii').get_data()
viewer = napari.view_image(img)

pix = segmentation.slic(img, n_segments=10000, compactness=0.002, multichannel=False,
                        )
pix_boundaries = segmentation.find_boundaries(pix)
viewer.add_labels(pix_boundaries)
