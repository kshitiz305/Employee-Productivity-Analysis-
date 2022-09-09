$(document).ready(function() {

	$('form').on('submit', function(event) {

		event.preventDefault();

		var formData = new FormData($('#formload');

		$.ajax({
			xhr : function() {
				var xhr = new window.XMLHttpRequest();

				xhr.upload.addEventListener('progress', function(e) {

					if (e.lengthComputable) {

						$('#loader').css({"display": "block"});

					}

				});

				return xhr;
			},
			type : 'POST',
			url : '/UpReport',
			data : formData,
			processData : false,
			contentType : false,
			success : function() {
				document.getElementById("loader").style.display = "none";
				
			}
		});

	});

});