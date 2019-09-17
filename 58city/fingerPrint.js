var fingerPrint = {
    validArray: function(array) {
        return array.length == 2 ? true : false
    },
    formatStr: function(str) {
        if (typeof str == "undefined") {
            return ""
        } else {
            return str
        }
    },
    targetFingerprint: function(x, y) {
        if (!this.validArray(x)) {
            if (this.validArray(y)) {
                return y
            } else {
                return []
            }
        } else {
            if (this.validArray(y)) {
                return parseInt(x[1]) > parseInt(y[1]) ? x : y
            } else {
                return x
            }
        }
    },
    set: function(result) {
        var fingerprintval = result.data.fingerprint;
        var fingerprintkey = "fingerprint";
        var ppStoretime = (new Date).getTime();
        ppStore.set(fingerprintkey, fingerprintval + "＿" + ppStoretime)
    },
    get: function() {
        var fingerprintkey = "fingerprint";
        var getFingerprintval = ppStore.get(fingerprintkey);
        var flashStore = getFingerprintval.flashStore;
        var localStore = getFingerprintval.localStore;
        var cookieStore = getFingerprintval.cookieStore;
        flashStore = this.formatStr(flashStore);
        localStore = this.formatStr(localStore);
        cookieStore = this.formatStr(cookieStore);
        var flashStoreArray = flashStore.split("＿");
        var localStoreArray = localStore.split("＿");
        var cookieStoreArray = cookieStore.split("＿");
        var flashStoreState, localStoreState, cookieStoreState;
        if (!this.validArray(flashStoreArray)) {
            flashStoreState = "0"
        } else {
            flashStoreState = "1"
        }
        if (!this.validArray(localStoreArray)) {
            localStoreState = "0"
        } else {
            localStoreState = "1"
        }
        if (!this.validArray(cookieStoreArray)) {
            cookieStoreState = "0"
        } else {
            cookieStoreState = "1"
        }
        var resultArray = this.targetFingerprint(this.targetFingerprint(flashStoreArray, localStoreArray), cookieStoreArray);
        if (resultArray.length == 0) {
            resultArray[0] = ""
        }
        if (this.validArray(resultArray)) {
            ppStore.clear(fingerprintkey);
            var ppStoretime = (new Date).getTime();
            ppStore.set(fingerprintkey, resultArray[0] + "＿" + ppStoretime)
        }
        var fingerprintState = flashStoreState + localStoreState + cookieStoreState;
        if (resultArray[0] == "undefined") {
            resultArray[0] = "";
            ppStore.clear(fingerprintkey)
        }
        if (document.getElementById("fingerprint")) {
            document.getElementById("fingerprint").value = resultArray[0] + "_" + fingerprintState
        }
        return resultArray[0] + "_" + fingerprintState
    },
    getnew: function() {
        var fingerprintkey = "finger_session";
        var cookieStore = document.cookie.match(new RegExp(fingerprintkey + "=([^&;]+)"));
        try {
            if (document.getElementById("fingerprint")) {
                document.getElementById("fingerprint").value = cookieStore[1]
            }
            return cookieStore[1]
        } catch (e) {
            return "111_000"
        }
    }
};

function getFingerPrint() {
    return fingerPrint.getnew()
}
console.log(getFingerPrint());