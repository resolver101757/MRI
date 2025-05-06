import os
import shutil
import json
from pathlib import Path
import argparse

def prepare_for_vlm(input_dir, output_dir, series_filter=None, max_images=None):
    """
    Prepare extracted MRI images for VLM analysis
    
    Args:
        input_dir: Path to directory containing extracted images
        output_dir: Path to output directory for VLM-ready data
        series_filter: Optional list of series names to include (if None, include all)
        max_images: Maximum number of images to include per series (if None, include all)
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Get all series directories
    all_series_dirs = [d for d in input_path.iterdir() if d.is_dir() and d.name != "anonymized_dicoms"]
    
    # Filter series if requested
    if series_filter:
        series_dirs = [d for d in all_series_dirs if any(filter_name.lower() in d.name.lower() for filter_name in series_filter)]
        print(f"Filtered from {len(all_series_dirs)} to {len(series_dirs)} series based on filter: {series_filter}")
    else:
        series_dirs = all_series_dirs
    
    # Create summary JSON
    summary = {
        "dataset_info": {
            "total_series": len(series_dirs),
            "source_dir": str(input_path),
            "series": []
        }
    }
    
    # Process each series
    for series_dir in series_dirs:
        series_name = series_dir.name
        
        # Create directory for this series
        series_output_dir = output_path / series_name
        series_output_dir.mkdir(exist_ok=True)
        
        # Read series info
        series_info = {}
        info_file = series_dir / "series_info.txt"
        if info_file.exists():
            with open(info_file, 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        series_info[key.strip()] = value.strip()
        
        # Copy series info file
        shutil.copy(info_file, series_output_dir / "series_info.txt")
        
        # Get image files
        image_files = sorted(list(series_dir.glob("slice_*.png")))
        
        # Apply max_images limit if specified
        if max_images and len(image_files) > max_images:
            # Take evenly spaced samples
            indices = [int(i * (len(image_files) - 1) / (max_images - 1)) for i in range(max_images)]
            selected_images = [image_files[i] for i in indices]
            print(f"Limiting {series_name} from {len(image_files)} to {len(selected_images)} images")
        else:
            selected_images = image_files
        
        # Add series info to summary
        series_summary = {
            "name": series_name,
            "total_images": len(image_files),
            "selected_images": len(selected_images),
            "metadata": series_info,
            "images": []
        }
        
        # Process each selected image
        for img_file in selected_images:
            # Get metadata
            metadata_file = img_file.parent / f"{img_file.stem}_metadata.txt"
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    for line in f:
                        if ':' in line:
                            key, value = line.strip().split(':', 1)
                            metadata[key.strip()] = value.strip()
            
            # Copy image file
            dest_img_file = series_output_dir / img_file.name
            shutil.copy(img_file, dest_img_file)
            
            # Create JSON metadata for this image
            img_metadata = {
                "filename": img_file.name,
                "metadata": metadata,
                "series_name": series_name
            }
            
            # Save individual image metadata
            with open(series_output_dir / f"{img_file.stem}.json", 'w') as f:
                json.dump(img_metadata, f, indent=2)
            
            # Add to series summary
            series_summary["images"].append({
                "filename": img_file.name,
                "metadata": metadata
            })
        
        # Add to overall summary
        summary["dataset_info"]["series"].append(series_summary)
    
    # Save overall summary
    with open(output_path / "dataset_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Create a simple guide for using with VLMs
    vlm_guide = """# Using This MRI Dataset with Vision Language Models

## Dataset Structure

This dataset contains MRI images organized by series. Each series represents a specific MRI sequence or view.

- Each series has its own directory
- PNG images are ready for direct input to VLMs
- JSON metadata files provide context for each image
- `dataset_summary.json` contains an overview of the entire dataset

## Tips for VLM Analysis

1. **Provide context**: Include the series information when analyzing images
2. **Include metadata**: Use the JSON metadata to provide context about each image
3. **Sequence understanding**: MRI scans are 3D volumes sliced into 2D images. The sequence of images is important.
4. **Multi-view analysis**: Consider using different series (sequences) of the same anatomy for more comprehensive analysis

## Example Prompts for VLMs

Example 1: "Analyze this MRI image. It's from the {series_name} series, which is {series_description}. The image is slice {slice_number} at location {slice_location}."

Example 2: "Compare these two MRI images from different sequences of the same anatomy. The first is a {series1_name} and the second is a {series2_name}."

Example 3: "Review this sequence of MRI images from the {series_name} series and describe what you observe."

"""
    
    with open(output_path / "vlm_guide.md", 'w') as f:
        f.write(vlm_guide)
    
    print(f"Prepared {len(series_dirs)} series for VLM analysis in {output_dir}")
    print(f"Total images: {sum(len(s['images']) for s in summary['dataset_info']['series'])}")
    print(f"See {output_path/'dataset_summary.json'} for complete dataset information")
    print(f"See {output_path/'vlm_guide.md'} for guidance on using with VLMs")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare MRI images for VLM analysis")
    parser.add_argument("--input", default=r"D:\personal\scans\mri\extracted_for_vlm", 
                        help="Input directory containing extracted MRI images")
    parser.add_argument("--output", default=r"D:\personal\scans\mri\vlm_ready", 
                        help="Output directory for VLM-ready dataset")
    parser.add_argument("--series", nargs="*", help="Optional filter for series names (substrings)")
    parser.add_argument("--max", type=int, help="Maximum number of images per series")
    
    args = parser.parse_args()
    
    prepare_for_vlm(args.input, args.output, args.series, args.max) 