// n8n Code Node: Convert Markdown Base64 to Binary
// Place this BEFORE the "Upload Markdown to Google Drive" node

// Get the base64 markdown data from HTTP Request response
const markdownBase64 = items[0].json.markdownData;
const markdownFileName = items[0].json.markdownFileName;

// Get folder ID from the Create Output Folder node
const folderId = $('CREATE OUTPUT FOLDER').first().json.id;

// Convert base64 to binary
const binaryData = Buffer.from(markdownBase64, 'base64');

// Return in n8n binary format
return [{
  json: {
    fileName: markdownFileName,
    folderId: folderId,
    success: items[0].json.success,
    language: items[0].json.language
  },
  binary: {
    data: {
      data: binaryData.toString('base64'),
      mimeType: 'text/markdown',
      fileName: markdownFileName,
      fileExtension: 'md'
    }
  }
}];
