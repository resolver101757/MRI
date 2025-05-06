import os
from pathlib import Path
import glob
import json
import shutil

def create_html_report(input_dir, output_file):
    """
    Create an HTML report of the extracted DICOM images
    
    Args:
        input_dir: Path to directory containing extracted images
        output_file: Path to output HTML file
    """
    input_path = Path(input_dir)
    
    # Get all series directories
    series_dirs = [d for d in input_path.iterdir() if d.is_dir() and d.name != "anonymized_dicoms"]
    
    # Start HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MRI Series Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1, h2, h3 {
                color: #333;
            }
            .series {
                margin-bottom: 30px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 20px;
            }
            .series-info {
                background-color: #f9f9f9;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            .thumbnail-container {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .thumbnail {
                width: 150px;
                text-align: center;
            }
            .thumbnail img {
                max-width: 150px;
                max-height: 150px;
                border: 1px solid #ddd;
            }
            .thumbnail p {
                margin: 5px 0;
                font-size: 12px;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>MRI Series Report</h1>
            <p>This report shows the extracted MRI series and sample images from each series.</p>
    """
    
    # Create a report dir for images
    report_dir = Path(output_file).parent / "report_files"
    report_dir.mkdir(exist_ok=True, parents=True)
    
    # Process each series
    for series_dir in series_dirs:
        series_name = series_dir.name
        
        # Read series info
        series_info = {}
        info_file = series_dir / "series_info.txt"
        if info_file.exists():
            with open(info_file, 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        series_info[key.strip()] = value.strip()
        
        # Get image files
        image_files = sorted(list(series_dir.glob("*.png")))
        
        # Skip if no images
        if not image_files:
            continue
        
        # Add series to HTML
        html_content += f"""
        <div class="series">
            <h2>{series_name}</h2>
            <div class="series-info">
        """
        
        # Add series info
        for key, value in series_info.items():
            html_content += f"<p><strong>{key}:</strong> {value}</p>\n"
        
        html_content += "</div>\n"
        
        # Sample images (first, middle, last)
        html_content += "<h3>Sample Images</h3>\n"
        html_content += '<div class="thumbnail-container">\n'
        
        # Determine which images to show
        if len(image_files) <= 9:
            sample_images = image_files
        else:
            # Take 9 evenly spaced images
            indices = [int(i * (len(image_files) - 1) / 8) for i in range(9)]
            sample_images = [image_files[i] for i in indices]
        
        # Add sample images
        for img_file in sample_images:
            # Get metadata
            metadata_file = img_file.parent / f"{img_file.stem}_metadata.txt"
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    for line in f:
                        if ':' in line:
                            key, value = line.strip().split(':', 1)
                            metadata[key.strip()] = value.strip()
            
            # Copy image to report directory
            img_copy_path = f"report_files/{series_name}_{img_file.name}"
            shutil.copy(img_file, report_dir / f"{series_name}_{img_file.name}")
            
            # Add to HTML
            html_content += f"""
            <div class="thumbnail">
                <img src="{img_copy_path}" alt="{img_file.name}">
                <p>{img_file.name}</p>
            """
            
            # Add slice location if available
            if "Slice Location" in metadata:
                html_content += f"<p>Location: {metadata['Slice Location']}</p>"
            
            if "Instance Number" in metadata:
                html_content += f"<p>Instance: {metadata['Instance Number']}</p>"
                
            html_content += "</div>\n"
        
        html_content += "</div>\n"  # Close thumbnail container
        
        # Add link to all images
        html_content += f"<p><a href='{series_dir}'>View all images in this series</a></p>\n"
        
        html_content += "</div>\n"  # Close series div
    
    # Close HTML
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML report created: {output_file}")

if __name__ == "__main__":
    # Path to extracted images
    input_dir = r"D:\personal\scans\mri\extracted_for_vlm"
    
    # Path to output HTML file
    output_file = r"D:\personal\scans\mri\mri_report.html"
    
    create_html_report(input_dir, output_file) 