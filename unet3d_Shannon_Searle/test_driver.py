# test_driver.py
import os
import torch
from dataset import CustomDataset, Resize3D, Normalize3D
from torchvision import transforms
from torch.utils.data import DataLoader
from train import Trainer
from predict import evaluate_dice_on_test_set

os.environ['TQDM_DISABLE'] = 'True'

def main():
    # Construct file paths correctly
    img_dir = "Labelled_weekly_MR_images_of_the_male_pelvis-QEzDvqEq-/data/semantic_MRs_anon"
    labels_dir = "Labelled_weekly_MR_images_of_the_male_pelvis-QEzDvqEq-/data/semantic_labels_anon"
    # Check if the directories exist
    if not os.path.exists(img_dir):
        print(f"Image directory {img_dir} does not exist.")
    if not os.path.exists(labels_dir):
        print(f"Labels directory {labels_dir} does not exist.")
    
    # Proceed with data loading if paths are correct
    image_filenames = [f for f in os.listdir(img_dir) if f.endswith('.nii.gz')]
    
    # Define transformations
    transform = transforms.Compose([
        Resize3D((64, 64, 32)),  # Resize to (depth, height, width)
        Normalize3D()  # Normalize the images
    ])
    
    # Create dataset
    dataset= CustomDataset(image_filenames, img_dir, labels_dir, transform = transform)
    
    # Split into training and test sets
    train_size = int(0.7 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

    # DataLoader for batching
    batch_size = 2
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=4)

    # Train the model
    print("Starting model training...")
    trainer = Trainer(train_loader)
    trained_model = trainer.train(n_epochs=1)
    
    # Test the model
    print("\nStarting model testing...")
    avg_dice_score, min_coeff = evaluate_dice_on_test_set(trained_model, test_loader)
    print(f"Average Dice Similarity Coefficient on Test Set: {avg_dice_score:.4f}")
    print(f"All Labels had a Minimum Similarity Coefficient of 0.7: {min_coeff}")

    
if __name__ == "__main__":
    main()