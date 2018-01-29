function toggle() {
  document.getElementById('login').style.display = "none";
  document.getElementById('key_form').style.display = "block";
}
function sendkey(){
  key = document.getElementById('key').value;

  if(key == "")
    return;
  var xhttp = new XMLHttpRequest();
  var fd = new FormData();
  fd.append("key",key);
  xhttp.onreadystatechange = function() {
    if(xhttp.status == 200 && xhttp.readyState == 4){
         showMessage("Data is uploaded to Google Drive", "Success");
    }
    else if(xhttp.status == 500){
        showMessage("Some error occurred while upload. Regenerate Key", "Failed")
    }
  };
  document.getElementById('submit').classList.toggle("loading");
  document.getElementById('submit').classList.toggle("disabled");

  //return;
  xhttp.open("POST","/backup/");
  xhttp.send(fd);
  }
