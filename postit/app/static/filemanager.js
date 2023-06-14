$(document).ready(function() {
    var editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
        lineNumbers: true,
        lineWrapping: true,
	mode: "python" // change this to the mode you want
    });
    $('#chat-form').on('submit', function(event) {
    event.preventDefault();
    var promptext = $('#prompt').val();
    var system = $('#system').val();
    var doc = editor.getDoc();
    var context=doc.getValue();
    var data = {
       'system': system,
       'prompt': promptext,
       'context':context
    };
if(promptext.trim() == "") {
    alert("Prompt cannot be empty");
} else {
   var doc = editor.getDoc();
   var lastLine=doc.lineCount();
   $.ajax({
        url: '/chat',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),

        success: function(response) {
             console.log(response);
             var doc = editor.getDoc();
             var lastLine=doc.lineCount()-1;
	     doc.replaceRange( "AI: "+response, {line: lastLine, ch: 0}, {line: lastLine, ch: editor.getLine(lastLine).length});
        }
    });
    
   doc.replaceRange("\n\nHuman: "+promptext+"\nThinking...",  {line: lastLine, ch: 0}, {line: lastLine, ch: 0});
}
});


	var dropZone = document.getElementById('drop_zone');
dropZone.addEventListener('dragenter', function() {
  this.classList.add('dragover');
});

dropZone.addEventListener('dragleave', function() {
  this.classList.remove('dragover');
});

dropZone.addEventListener('drop', function(event) {
  event.preventDefault();
  this.classList.remove('dragover');
  // handle the dropped file(s) here
});
dropZone.addEventListener('drop', function(event) {
    event.preventDefault();
    this.classList.remove('dragover');
    // handle file upload
});
    $("#submitForm").on("submit", function(e) {
        e.preventDefault();
        var filename = $("#filename").val();
        var fileUpload = $("#fileUpload").get(0).files[0];
        var data = new FormData();
        data.append('filename', filename);
        if (fileUpload) {
            data.append('file', fileUpload);
        } else {
            data.append('text', editor.getValue());
        }
        $.ajax({
            url: '/',
            type: 'POST',
            processData: false, // required for file uploading
            contentType: false, // required for file uploading
            data: data,
            success: function() {
                location.reload();
            },
            error: function(xhr) {
                if (xhr.status == 409) {
                    if (confirm(xhr.responseJSON.error + ' Do you want to overwrite it?')) {
                        $.ajax({
                            url: '/',
                            type: 'POST',
                            processData: false,
                            contentType: false,
                            data: data,
                            success: function() {
                                location.reload();
                            }
                        });
                    }
                }
            }
        });
    });

    $("#clear").on("click", function() {
        $("#filename").val('');
        editor.setValue('');
    });

    var currentFile;
    $(".file-item").on("contextmenu", function(e) {
        e.preventDefault();
        currentFile = $(this).find(".file-name").text();
        $("#contextMenu").css({
            display: "block",
            left: e.pageX,
            top: e.pageY
        });
    });

    $("#loadFile").on("click", function() {
        $.ajax({
            url: '/load',
            type: 'POST',
            data: {
                filename: currentFile
            },
            success: function(data) {
                $("#filename").val(currentFile);
                editor.setValue(data);
                $("#contextMenu").hide();
            }
        });
    });

    $("#deleteFile").on("click", function() {
        $.ajax({
            url: '/delete',
            type: 'POST',
            data: {
                filename: currentFile
            },
            success: function() {
                location.reload();
            }
        });
    });

    // Hide the context menu when clicking outside it
    $(document).on("click", function(e) {
        if ($(e.target).closest("#contextMenu").length === 0) {
            $("#contextMenu").hide();
        }
    });

    // Download file on left click
    $(".file-item").on("click", function() {
        var filename = $(this).find(".file-name").text();
        window.location.href = "/download/" + filename;
    });

    document.getElementById('drop_zone').addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();

        var files = e.dataTransfer.files;

        for (var i = 0, f; f = files[i]; i++) {
            uploadFile(f);
        }
    }, false);

    document.getElementById('drop_zone').addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
    }, false);

function uploadFile(file) {
    var url = '/';
    var xhr = new XMLHttpRequest();
    var data = new FormData();
    data.append('file', file);
    
 $.ajax({
            url: '/',
            type: 'POST',
            processData: false, // required for file uploading
            contentType: false, // required for file uploading
            data: data,
            success: function() {
                location.reload();
            },
            error: function(xhr) {
                if (xhr.status == 409) {
                    if (confirm(xhr.responseJSON.error + ' Do you want to overwrite it?')) {
                        $.ajax({
                            url: '/',
                            type: 'POST',
                            processData: false,
                            contentType: false,
                            data: data,
                            success: function() {
                                location.reload();
                            }
                        });
                    }
                }
            }
        });

}
   var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
} 

});

