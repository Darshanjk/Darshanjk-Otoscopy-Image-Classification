$(document).ready(function() {
    $('#upload-form').on('submit', function(e) {
        e.preventDefault();
        
        // Clear previous errors
        $('#error-message').addClass('d-none').text('');
        
        // Show loading spinner
        $('#loading-spinner').removeClass('d-none');
        
        // Disable submit button
        $('#submit-button').prop('disabled', true);
        
        var formData = new FormData();
        var fileInput = $('#imageUpload')[0];
        
        // Validate file
        if (fileInput.files.length === 0) {
            showError('Please select an image file');
            return;
        }
        
        var file = fileInput.files[0];
        
        // Validate file type
        if (!file.type.match('image.*')) {
            showError('Please select an image file (PNG, JPG, or JPEG)');
            return;
        }
        
        formData.append('file', file);

        $.ajax({
            url: '/predict',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if(response.error) {
                    showError(response.error);
                    return;
                }
                
                // Update results
                $('#prediction-text').text('Detected Disease: ' + response.prediction);
                $('#confidence-text').text('Confidence: ' + response.confidence.toFixed(2) + '%');
                $('#uploaded-image').attr('src', '/static/' + response.image_path);
                $('#result').removeClass('d-none');
            },
            error: function(xhr, status, error) {
                let errorMessage = 'Error occurred during prediction';
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.error) {
                        errorMessage = response.error;
                    }
                } catch (e) {
                    console.error('Error parsing error response:', e);
                }
                showError(errorMessage);
            },
            complete: function() {
                // Hide loading spinner
                $('#loading-spinner').addClass('d-none');
                // Enable submit button
                $('#submit-button').prop('disabled', false);
            }
        });
    });

    function showError(message) {
        $('#error-message')
            .removeClass('d-none')
            .addClass('alert alert-danger')
            .text(message);
        
        // Hide loading spinner
        $('#loading-spinner').addClass('d-none');
        // Enable submit button
        $('#submit-button').prop('disabled', false);
    }
});
