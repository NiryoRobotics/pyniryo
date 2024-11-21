function _getJSONFile(url) {
  return new Promise(function (resolve, reject) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onload = function () {
      if (this.status >= 200 && this.status < 300) {
        resolve(xhr.response)
      } else {
        reject({
          status: this.status,
          statusText: xhr.response
        });
      }
    };
    xhr.onerror = function () {
      reject({
        status: this.status,
        statusText: xhr.statusText
      });
    }
    xhr.send();
  });
}

var available_versions = [];

function _retrieveLatestVersionFromArray(versions_array) {
  // Default value
  let latest_version = "0.0.0";
  let counter = -1;
  while (++counter < versions_array.length) {
    // localeCompare < 0 means version tested is greater than latest_version
    if (latest_version.localeCompare(versions_array[counter], undefined, { numeric: true, sensitivity: 'base' }) < 0) {
      latest_version = versions_array[counter];
    }
  }
  return latest_version;
}

function retrieveVersionArray(base_url) {
  return new Promise(function (resolve, reject) {
    _getJSONFile(base_url + "/versions.json").then(function (response) {
      if (response.hasOwnProperty("versions")) {
        available_versions = response["versions"];
      }
      resolve(available_versions);
    }).catch(function (err) {
      reject(err);
    })
  })
}

function tryToRedirectTo(base_url, version, language, page_name) {
  var toTest = base_url + "/" + version + "/" + language + "/" + page_name + ".html";
  var request = new XMLHttpRequest();
  request.open('GET', toTest, true);
  request.onreadystatechange = function () {
    if (request.readyState === 4) {
      if (request.status === 404) {
        window.location.href = base_url + "/" + version + "/" + language;
      } else {
        window.location.href = toTest;
      }
    }
  };
  request.send();
}

function translateDoc(target_language) {
  const current_language = document.documentElement.lang;
  const current_url = window.location.href;
  if (current_language == target_language) {
    return ;
  } else {
    window.location.href = current_url.replace("/" + current_language + "/", "/" + target_language + "/");
  }
}