// n8n Code Node: Convert Image Base64 to Binary
// Place this AFTER the "Split Out" node and BEFORE "Upload Images to Google Drive"

// Get folder ID from the Create Output Folder node
const folderId = $('CREATE OUTPUT FOLDER').first().json.id;

// Process ALL items, not just the first one
const results = [];

for (let i = 0; i < items.length; i++) {
  const item = items[i];

  // Get the base64 image data from the current item
  const imageBase64 = item.json.data;
  const imageFileName = item.json.fileName;

  // Check if data exists
  if (!imageBase64) {
    throw new Error(`No image data found in item ${i}. Item structure: ${JSON.stringify(item.json)}`);
  }

  // Convert base64 to binary
  const binaryData = Buffer.from(imageBase64, 'base64');

  // Add to results
  results.push({
    json: {
      fileName: imageFileName,
      folderId: folderId
    },
    binary: {
      data: {
        data: binaryData.toString('base64'),
        mimeType: 'image/png',
        fileName: imageFileName,
        fileExtension: 'png'
      }
    }
  });
}

// Return ALL processed items
return results;
