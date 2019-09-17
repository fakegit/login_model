navigator = {
    // WT-JS_DEBUG v1.7.5 - NLiger2018
    appCodeName: "Mozilla",
    appMinorVersion: "0",
    appName: "Netscape",
    appVersion: "5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    browserLanguage: "zh-CN",
    cookieEnabled: true,
    cpuClass: "x86",
    language: "zh-CN",
    maxTouchPoints: 0,
    msManipulationViewsEnabled: true,
    msMaxTouchPoints: 0,
    msPointerEnabled: true,
    onLine: true,
    platform: "Win32",
    pointerEnabled: true,
    product: "Gecko",
    systemLanguage: "zh-CN",
    userAgent: "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    userLanguage: "zh-CN",
    vendor: "",
    vendorSub: "",
    webdriver: false
}, window = this, window.navigator = navigator;

function safe_add(x, y) {
    var lsw = (x & 65535) + (y & 65535)
        , msw = (x >> 16) + (y >> 16) + (lsw >> 16);
    return msw << 16 | lsw & 65535
}
function bit_rol(num, cnt) {
    return num << cnt | num >>> 32 - cnt
}
function md5_cmn(q, a, b, x, s, t) {
    return safe_add(bit_rol(safe_add(safe_add(a, q), safe_add(x, t)), s), b)
}
function md5_ff(a, b, c, d, x, s, t) {
    return md5_cmn(b & c | ~b & d, a, b, x, s, t)
}
function md5_gg(a, b, c, d, x, s, t) {
    return md5_cmn(b & d | c & ~d, a, b, x, s, t)
}
function md5_hh(a, b, c, d, x, s, t) {
    return md5_cmn(b ^ c ^ d, a, b, x, s, t)
}
function md5_ii(a, b, c, d, x, s, t) {
    return md5_cmn(c ^ (b | ~d), a, b, x, s, t)
}
function binl_md5(x, len) {
    x[len >> 5] |= 128 << len % 32;
    x[(len + 64 >>> 9 << 4) + 14] = len;
    var i, olda, oldb, oldc, oldd, a = 1732584193, b = -271733879, c = -1732584194, d = 271733878;
    for (i = 0; i < x.length; i += 16) {
        olda = a;
        oldb = b;
        oldc = c;
        oldd = d;
        a = md5_ff(a, b, c, d, x[i], 7, -680876936);
        d = md5_ff(d, a, b, c, x[i + 1], 12, -389564586);
        c = md5_ff(c, d, a, b, x[i + 2], 17, 606105819);
        b = md5_ff(b, c, d, a, x[i + 3], 22, -1044525330);
        a = md5_ff(a, b, c, d, x[i + 4], 7, -176418897);
        d = md5_ff(d, a, b, c, x[i + 5], 12, 1200080426);
        c = md5_ff(c, d, a, b, x[i + 6], 17, -1473231341);
        b = md5_ff(b, c, d, a, x[i + 7], 22, -45705983);
        a = md5_ff(a, b, c, d, x[i + 8], 7, 1770035416);
        d = md5_ff(d, a, b, c, x[i + 9], 12, -1958414417);
        c = md5_ff(c, d, a, b, x[i + 10], 17, -42063);
        b = md5_ff(b, c, d, a, x[i + 11], 22, -1990404162);
        a = md5_ff(a, b, c, d, x[i + 12], 7, 1804603682);
        d = md5_ff(d, a, b, c, x[i + 13], 12, -40341101);
        c = md5_ff(c, d, a, b, x[i + 14], 17, -1502002290);
        b = md5_ff(b, c, d, a, x[i + 15], 22, 1236535329);
        a = md5_gg(a, b, c, d, x[i + 1], 5, -165796510);
        d = md5_gg(d, a, b, c, x[i + 6], 9, -1069501632);
        c = md5_gg(c, d, a, b, x[i + 11], 14, 643717713);
        b = md5_gg(b, c, d, a, x[i], 20, -373897302);
        a = md5_gg(a, b, c, d, x[i + 5], 5, -701558691);
        d = md5_gg(d, a, b, c, x[i + 10], 9, 38016083);
        c = md5_gg(c, d, a, b, x[i + 15], 14, -660478335);
        b = md5_gg(b, c, d, a, x[i + 4], 20, -405537848);
        a = md5_gg(a, b, c, d, x[i + 9], 5, 568446438);
        d = md5_gg(d, a, b, c, x[i + 14], 9, -1019803690);
        c = md5_gg(c, d, a, b, x[i + 3], 14, -187363961);
        b = md5_gg(b, c, d, a, x[i + 8], 20, 1163531501);
        a = md5_gg(a, b, c, d, x[i + 13], 5, -1444681467);
        d = md5_gg(d, a, b, c, x[i + 2], 9, -51403784);
        c = md5_gg(c, d, a, b, x[i + 7], 14, 1735328473);
        b = md5_gg(b, c, d, a, x[i + 12], 20, -1926607734);
        a = md5_hh(a, b, c, d, x[i + 5], 4, -378558);
        d = md5_hh(d, a, b, c, x[i + 8], 11, -2022574463);
        c = md5_hh(c, d, a, b, x[i + 11], 16, 1839030562);
        b = md5_hh(b, c, d, a, x[i + 14], 23, -35309556);
        a = md5_hh(a, b, c, d, x[i + 1], 4, -1530992060);
        d = md5_hh(d, a, b, c, x[i + 4], 11, 1272893353);
        c = md5_hh(c, d, a, b, x[i + 7], 16, -155497632);
        b = md5_hh(b, c, d, a, x[i + 10], 23, -1094730640);
        a = md5_hh(a, b, c, d, x[i + 13], 4, 681279174);
        d = md5_hh(d, a, b, c, x[i], 11, -358537222);
        c = md5_hh(c, d, a, b, x[i + 3], 16, -722521979);
        b = md5_hh(b, c, d, a, x[i + 6], 23, 76029189);
        a = md5_hh(a, b, c, d, x[i + 9], 4, -640364487);
        d = md5_hh(d, a, b, c, x[i + 12], 11, -421815835);
        c = md5_hh(c, d, a, b, x[i + 15], 16, 530742520);
        b = md5_hh(b, c, d, a, x[i + 2], 23, -995338651);
        a = md5_ii(a, b, c, d, x[i], 6, -198630844);
        d = md5_ii(d, a, b, c, x[i + 7], 10, 1126891415);
        c = md5_ii(c, d, a, b, x[i + 14], 15, -1416354905);
        b = md5_ii(b, c, d, a, x[i + 5], 21, -57434055);
        a = md5_ii(a, b, c, d, x[i + 12], 6, 1700485571);
        d = md5_ii(d, a, b, c, x[i + 3], 10, -1894986606);
        c = md5_ii(c, d, a, b, x[i + 10], 15, -1051523);
        b = md5_ii(b, c, d, a, x[i + 1], 21, -2054922799);
        a = md5_ii(a, b, c, d, x[i + 8], 6, 1873313359);
        d = md5_ii(d, a, b, c, x[i + 15], 10, -30611744);
        c = md5_ii(c, d, a, b, x[i + 6], 15, -1560198380);
        b = md5_ii(b, c, d, a, x[i + 13], 21, 1309151649);
        a = md5_ii(a, b, c, d, x[i + 4], 6, -145523070);
        d = md5_ii(d, a, b, c, x[i + 11], 10, -1120210379);
        c = md5_ii(c, d, a, b, x[i + 2], 15, 718787259);
        b = md5_ii(b, c, d, a, x[i + 9], 21, -343485551);
        a = safe_add(a, olda);
        b = safe_add(b, oldb);
        c = safe_add(c, oldc);
        d = safe_add(d, oldd)
    }
    return [a, b, c, d]
}
function binl2rstr(input) {
    var i, output = "";
    for (i = 0; i < input.length * 32; i += 8) {
        output += String.fromCharCode(input[i >> 5] >>> i % 32 & 255)
    }
    return output
}
function rstr2binl(input) {
    var i, output = [];
    output[(input.length >> 2) - 1] = undefined;
    for (i = 0; i < output.length; i += 1) {
        output[i] = 0
    }
    for (i = 0; i < input.length * 8; i += 8) {
        output[i >> 5] |= (input.charCodeAt(i / 8) & 255) << i % 32
    }
    return output
}
function rstr_md5(s) {
    return binl2rstr(binl_md5(rstr2binl(s), s.length * 8))
}
function rstr_hmac_md5(key, data) {
    var i, bkey = rstr2binl(key), ipad = [], opad = [], hash;
    ipad[15] = opad[15] = undefined;
    if (bkey.length > 16) {
        bkey = binl_md5(bkey, key.length * 8)
    }
    for (i = 0; i < 16; i += 1) {
        ipad[i] = bkey[i] ^ 909522486;
        opad[i] = bkey[i] ^ 1549556828
    }
    hash = binl_md5(ipad.concat(rstr2binl(data)), 512 + data.length * 8);
    return binl2rstr(binl_md5(opad.concat(hash), 512 + 128))
}
function rstr2hex(input) {
    var hex_tab = "0123456789abcdef", output = "", x, i;
    for (i = 0; i < input.length; i += 1) {
        x = input.charCodeAt(i);
        output += hex_tab.charAt(x >>> 4 & 15) + hex_tab.charAt(x & 15)
    }
    return output
}
function str2rstr_utf8(input) {
    return unescape(encodeURIComponent(input))
}
function raw_md5(s) {
    return rstr_md5(str2rstr_utf8(s))
}
function hex_md5(s) {
    return rstr2hex(raw_md5(s))
}
function raw_hmac_md5(k, d) {
    return rstr_hmac_md5(str2rstr_utf8(k), str2rstr_utf8(d))
}
function hex_hmac_md5(k, d) {
    return rstr2hex(raw_hmac_md5(k, d))
}
function md5(string, key, raw) {
    if (!key) {
        if (!raw) {
            return hex_md5(string)
        }
        return raw_md5(string)
    }
    if (!raw) {
        return hex_hmac_md5(key, string)
    }
    return raw_hmac_md5(key, string)
}

var Fingerprint2 = function(options) {
    if (!(this instanceof Fingerprint2)) {
        return new Fingerprint2(options)
    }
    var defaultOptions = {
        swfContainerId: "fingerprintjs2",
        swfPath: "flash/compiled/FontList.swf",
        detectScreenOrientation: true,
        sortPluginsFor: [/palemoon/i],
        userDefinedFonts: []
    };
    this.options = this.extend(options, defaultOptions);
    this.nativeForEach = Array.prototype.forEach;
    this.nativeMap = Array.prototype.map
};
Fingerprint2.prototype = {
    extend: function (source, target) {
        if (source == null) {
            return target
        }
        for (var k in source) {
            if (source[k] != null && target[k] !== source[k]) {
                target[k] = source[k]
            }
        }
        return target
    },
    log: function (msg) {
        if (window.console) {
            console.log(msg)
        }
    },
    get: function (done) {
        var keys = [];
        var languageKey = this.languageKey(keys);
        var colorDepthKey = this.colorDepthKey(keys);
        var pixelRatioKey = this.pixelRatioKey(keys);
        var hardwareConcurrencyKey = this.hardwareConcurrencyKey(keys);
        var getScreenResolution = this.getScreenResolution(keys);
        var getAvailableScreenResolution = this.getAvailableScreenResolution(keys);
        var timezoneOffsetKey = this.timezoneOffsetKey(keys);
        var sessionStorageKey = this.sessionStorageKey(keys);
        var localStorageKey = this.localStorageKey(keys);
        var indexedDbKey = this.indexedDbKey(keys);
        var addBehaviorKey = this.addBehaviorKey(keys);
        var openDatabaseKey = this.openDatabaseKey(keys);
        var cpuClassKey = this.cpuClassKey(keys);
        var platformKey = this.platformKey(keys);
        var doNotTrackKey = this.doNotTrackKey(keys);
        var pluginsKey = this.pluginsKey(keys);
        var adBlockKey = this.adBlockKey(keys);
        var hasLiedLanguagesKey = this.hasLiedLanguagesKey(keys);
        var hasLiedResolutionKey = this.hasLiedResolutionKey(keys);
        var hasLiedOsKey = this.hasLiedOsKey(keys);
        var hasLiedBrowserKey = this.hasLiedBrowserKey(keys);
        var touchSupportKey = this.touchSupportKey(keys);
        var canvasKey = md5(this.canvasKey(keys));
        var webglKey = md5(this.webglKey(keys));
        var mydata = languageKey + "|" + colorDepthKey + "|" + pixelRatioKey + "|" + hardwareConcurrencyKey + "|" + getScreenResolution + "|" + getAvailableScreenResolution + "|" + timezoneOffsetKey + "|" + sessionStorageKey + "|" + localStorageKey + "|" + indexedDbKey + "|" + addBehaviorKey + "|" + openDatabaseKey + "|" + cpuClassKey + "|" + platformKey + "|" + doNotTrackKey + "|" + pluginsKey + "|" + adBlockKey + "|" + hasLiedLanguagesKey + "|" + hasLiedResolutionKey + "|" + hasLiedOsKey + "|" + hasLiedBrowserKey + "|" + touchSupportKey + "|" + canvasKey + "|" + webglKey;
        return mydata
    },
    userAgentKey: function (keys) {
        var user_agent;
        if (!this.options.excludeUserAgent) {
            user_agent = this.getUserAgent()
        }
        return user_agent
    },
    getUserAgent: function () {
        return navigator.userAgent
    },
    languageKey: function (keys) {
        var language;
        if (!this.options.excludeLanguage) {
            language = navigator.language || navigator.userLanguage || navigator.browserLanguage || navigator.systemLanguage || ""
        }
        return language
    },
    colorDepthKey: function (keys) {
        var color_depth;
        if (!this.options.excludeColorDepth) {
            color_depth = screen.colorDepth || -1
        }
        return color_depth
    },
    pixelRatioKey: function (keys) {
        var pixel_ratio;
        if (!this.options.excludePixelRatio) {
            pixel_ratio = this.getPixelRatio()
        }
        return pixel_ratio
    },
    getPixelRatio: function () {
        return window.devicePixelRatio || ""
    },
    getScreenResolution: function (keys) {
        var resolution;
        if (this.options.detectScreenOrientation) {
            resolution = screen.height > screen.width ? screen.height + "_" + screen.width : screen.width + "_" + screen.height
        } else {
            resolution = screen.width + "_" + screen.height
        }
        return resolution
    },
    getAvailableScreenResolution: function (keys) {
        var available;
        if (screen.availWidth && screen.availHeight) {
            if (this.options.detectScreenOrientation) {
                available = screen.availHeight > screen.availWidth ? screen.availHeight + "_" + screen.availWidth : screen.availWidth + "_" + screen.availHeight
            } else {
                available = screen.availHeight + "_" + screen.availWidth
            }
        }
        return available
    },
    timezoneOffsetKey: function (keys) {
        var timezone_offset;
        if (!this.options.excludeTimezoneOffset) {
            timezone_offset = (new Date).getTimezoneOffset()
        }
        return timezone_offset
    },
    sessionStorageKey: function (keys) {
        var sessionStorageKey;
        if (!this.options.excludeSessionStorage && this.hasSessionStorage()) {
            sessionStorageKey = 1
        }
        return sessionStorageKey
    },
    localStorageKey: function (keys) {
        var local_storage;
        if (!this.options.excludeSessionStorage && this.hasLocalStorage()) {
            local_storage = 1
        }
        return local_storage
    },
    indexedDbKey: function (keys) {
        var indexed_db;
        if (!this.options.excludeIndexedDB && this.hasIndexedDB()) {
            indexed_db = 1
        }
        return indexed_db
    },
    addBehaviorKey: function (keys) {
        var add_behavior;
        if (document.body && !this.options.excludeAddBehavior && document.body.addBehavior) {
            add_behavior = 1
        }
        return add_behavior
    },
    openDatabaseKey: function (keys) {
        var open_database;
        if (!this.options.excludeOpenDatabase && window.openDatabase) {
            open_database = 1
        }
        return open_database
    },
    cpuClassKey: function (keys) {
        var open_database;
        if (!this.options.excludeCpuClass) {
            open_database = this.getNavigatorCpuClass()
        }
        return open_database
    },
    platformKey: function (keys) {
        var navigator_platform;
        if (!this.options.excludePlatform) {
            navigator_platform = this.getNavigatorPlatform()
        }
        return navigator_platform
    },
    doNotTrackKey: function (keys) {
        var do_not_track;
        if (!this.options.excludeDoNotTrack) {
            do_not_track = this.getDoNotTrack()
        }
        return do_not_track
    },
    canvasKey: function (keys) {
        var canvas;
        if (!this.options.excludeCanvas && this.isCanvasSupported()) {
            canvas = this.getCanvasFp()
        }
        return keys
    },
    webglKey: function (keys) {
        if (this.options.excludeWebGL) {
            var webgl = "";
            if (typeof NODEBUG === "undefined") {
                this.log("Skipping WebGL fingerprinting per excludeWebGL configuration option")
            }
            return webgl
        }
        if (!this.isWebGlSupported()) {
            if (typeof NODEBUG === "undefined") {
                this.log("Skipping WebGL fingerprinting because it is not supported in this browser")
            }
            return webgl
        }
        webgl = this.getWebglFp();
        return webgl
    },
    adBlockKey: function (keys) {
        var adblock;
        if (!this.options.excludeAdBlock) {
            adblock = this.getAdBlock()
        }
        return adblock
    },
    hasLiedLanguagesKey: function (keys) {
        var has_lied_languages;
        if (!this.options.excludeHasLiedLanguages) {
            has_lied_languages = this.getHasLiedLanguages()
        }
        return has_lied_languages
    },
    hasLiedResolutionKey: function (keys) {
        var has_lied_resolution;
        if (!this.options.excludeHasLiedResolution) {
            has_lied_resolution = this.getHasLiedResolution()
        }
        return has_lied_resolution
    },
    hasLiedOsKey: function (keys) {
        var has_lied_os;
        if (!this.options.excludeHasLiedOs) {
            has_lied_os = this.getHasLiedOs()
        }
        return has_lied_os
    },
    hasLiedBrowserKey: function (keys) {
        var has_lied_browser;
        if (!this.options.excludeHasLiedBrowser) {
            has_lied_browser = this.getHasLiedBrowser()
        }
        return has_lied_browser
    },
    fontsKey: function (keys, done) {
        if (this.options.excludeJsFonts) {
            return this.flashFontsKey(keys, done)
        }
        return this.jsFontsKey(keys, done)
    },
    flashFontsKey: function (keys, done) {
        if (this.options.excludeFlashFonts) {
            if (typeof NODEBUG === "undefined") {
                this.log("Skipping flash fonts detection per excludeFlashFonts configuration option")
            }
            return done(keys)
        }
        if (!this.hasSwfObjectLoaded()) {
            if (typeof NODEBUG === "undefined") {
                this.log("Swfobject is not detected, Flash fonts enumeration is skipped")
            }
            return done(keys)
        }
        if (!this.hasMinFlashInstalled()) {
            if (typeof NODEBUG === "undefined") {
                this.log("Flash is not installed, skipping Flash fonts enumeration")
            }
            return done(keys)
        }
        if (typeof this.options.swfPath === "undefined") {
            if (typeof NODEBUG === "undefined") {
                this.log("To use Flash fonts detection, you must pass a valid swfPath option, skipping Flash fonts enumeration")
            }
            return done(keys)
        }
        this.loadSwfAndDetectFonts(function (fonts) {
            keys.push({
                key: "swf_fonts",
                value: fonts.join(";")
            });
            done(keys)
        })
    },
    jsFontsKey: function (keys, done) {
        var that = this;
        return setTimeout(function () {
            var baseFonts = ["monospace", "sans-serif", "serif"];
            var fontList = ["Andale Mono", "Arial", "Arial Black", "Arial Hebrew", "Arial MT", "Arial Narrow", "Arial Rounded MT Bold", "Arial Unicode MS", "Bitstream Vera Sans Mono", "Book Antiqua", "Bookman Old Style", "Calibri", "Cambria", "Cambria Math", "Century", "Century Gothic", "Century Schoolbook", "Comic Sans", "Comic Sans MS", "Consolas", "Courier", "Courier New", "Garamond", "Geneva", "Georgia", "Helvetica", "Helvetica Neue", "Impact", "Lucida Bright", "Lucida Calligraphy", "Lucida Console", "Lucida Fax", "LUCIDA GRANDE", "Lucida Handwriting", "Lucida Sans", "Lucida Sans Typewriter", "Lucida Sans Unicode", "Microsoft Sans Serif", "Monaco", "Monotype Corsiva", "MS Gothic", "MS Outlook", "MS PGothic", "MS Reference Sans Serif", "MS Sans Serif", "MS Serif", "MYRIAD", "MYRIAD PRO", "Palatino", "Palatino Linotype", "Segoe Print", "Segoe Script", "Segoe UI", "Segoe UI Light", "Segoe UI Semibold", "Segoe UI Symbol", "Tahoma", "Times", "Times New Roman", "Times New Roman PS", "Trebuchet MS", "Verdana", "Wingdings", "Wingdings 2", "Wingdings 3"];
            var extendedFontList = ["Abadi MT Condensed Light", "Academy Engraved LET", "ADOBE CASLON PRO", "Adobe Garamond", "ADOBE GARAMOND PRO", "Agency FB", "Aharoni", "Albertus Extra Bold", "Albertus Medium", "Algerian", "Amazone BT", "American Typewriter", "American Typewriter Condensed", "AmerType Md BT", "Andalus", "Angsana New", "AngsanaUPC", "Antique Olive", "Aparajita", "Apple Chancery", "Apple Color Emoji", "Apple SD Gothic Neo", "Arabic Typesetting", "ARCHER", "ARNO PRO", "Arrus BT", "Aurora Cn BT", "AvantGarde Bk BT", "AvantGarde Md BT", "AVENIR", "Ayuthaya", "Bandy", "Bangla Sangam MN", "Bank Gothic", "BankGothic Md BT", "Baskerville", "Baskerville Old Face", "Batang", "BatangChe", "Bauer Bodoni", "Bauhaus 93", "Bazooka", "Bell MT", "Bembo", "Benguiat Bk BT", "Berlin Sans FB", "Berlin Sans FB Demi", "Bernard MT Condensed", "BernhardFashion BT", "BernhardMod BT", "Big Caslon", "BinnerD", "Blackadder ITC", "BlairMdITC TT", "Bodoni 72", "Bodoni 72 Oldstyle", "Bodoni 72 Smallcaps", "Bodoni MT", "Bodoni MT Black", "Bodoni MT Condensed", "Bodoni MT Poster Compressed", "Bookshelf Symbol 7", "Boulder", "Bradley Hand", "Bradley Hand ITC", "Bremen Bd BT", "Britannic Bold", "Broadway", "Browallia New", "BrowalliaUPC", "Brush Script MT", "Californian FB", "Calisto MT", "Calligrapher", "Candara", "CaslonOpnface BT", "Castellar", "Centaur", "Cezanne", "CG Omega", "CG Times", "Chalkboard", "Chalkboard SE", "Chalkduster", "Charlesworth", "Charter Bd BT", "Charter BT", "Chaucer", "ChelthmITC Bk BT", "Chiller", "Clarendon", "Clarendon Condensed", "CloisterBlack BT", "Cochin", "Colonna MT", "Constantia", "Cooper Black", "Copperplate", "Copperplate Gothic", "Copperplate Gothic Bold", "Copperplate Gothic Light", "CopperplGoth Bd BT", "Corbel", "Cordia New", "CordiaUPC", "Cornerstone", "Coronet", "Cuckoo", "Curlz MT", "DaunPenh", "Dauphin", "David", "DB LCD Temp", "DELICIOUS", "Denmark", "DFKai-SB", "Didot", "DilleniaUPC", "DIN", "DokChampa", "Dotum", "DotumChe", "Ebrima", "Edwardian Script ITC", "Elephant", "English 111 Vivace BT", "Engravers MT", "EngraversGothic BT", "Eras Bold ITC", "Eras Demi ITC", "Eras Light ITC", "Eras Medium ITC", "EucrosiaUPC", "Euphemia", "Euphemia UCAS", "EUROSTILE", "Exotc350 Bd BT", "FangSong", "Felix Titling", "Fixedsys", "FONTIN", "Footlight MT Light", "Forte", "FrankRuehl", "Fransiscan", "Freefrm721 Blk BT", "FreesiaUPC", "Freestyle Script", "French Script MT", "FrnkGothITC Bk BT", "Fruitger", "FRUTIGER", "Futura", "Futura Bk BT", "Futura Lt BT", "Futura Md BT", "Futura ZBlk BT", "FuturaBlack BT", "Gabriola", "Galliard BT", "Gautami", "Geeza Pro", "Geometr231 BT", "Geometr231 Hv BT", "Geometr231 Lt BT", "GeoSlab 703 Lt BT", "GeoSlab 703 XBd BT", "Gigi", "Gill Sans", "Gill Sans MT", "Gill Sans MT Condensed", "Gill Sans MT Ext Condensed Bold", "Gill Sans Ultra Bold", "Gill Sans Ultra Bold Condensed", "Gisha", "Gloucester MT Extra Condensed", "GOTHAM", "GOTHAM BOLD", "Goudy Old Style", "Goudy Stout", "GoudyHandtooled BT", "GoudyOLSt BT", "Gujarati Sangam MN", "Gulim", "GulimChe", "Gungsuh", "GungsuhChe", "Gurmukhi MN", "Haettenschweiler", "Harlow Solid Italic", "Harrington", "Heather", "Heiti SC", "Heiti TC", "HELV", "Herald", "High Tower Text", "Hiragino Kaku Gothic ProN", "Hiragino Mincho ProN", "Hoefler Text", "Humanst 521 Cn BT", "Humanst521 BT", "Humanst521 Lt BT", "Imprint MT Shadow", "Incised901 Bd BT", "Incised901 BT", "Incised901 Lt BT", "INCONSOLATA", "Informal Roman", "Informal011 BT", "INTERSTATE", "IrisUPC", "Iskoola Pota", "JasmineUPC", "Jazz LET", "Jenson", "Jester", "Jokerman", "Juice ITC", "Kabel Bk BT", "Kabel Ult BT", "Kailasa", "KaiTi", "Kalinga", "Kannada Sangam MN", "Kartika", "Kaufmann Bd BT", "Kaufmann BT", "Khmer UI", "KodchiangUPC", "Kokila", "Korinna BT", "Kristen ITC", "Krungthep", "Kunstler Script", "Lao UI", "Latha", "Leelawadee", "Letter Gothic", "Levenim MT", "LilyUPC", "Lithograph", "Lithograph Light", "Long Island", "Lydian BT", "Magneto", "Maiandra GD", "Malayalam Sangam MN", "Malgun Gothic", "Mangal", "Marigold", "Marion", "Marker Felt", "Market", "Marlett", "Matisse ITC", "Matura MT Script Capitals", "Meiryo", "Meiryo UI", "Microsoft Himalaya", "Microsoft JhengHei", "Microsoft New Tai Lue", "Microsoft PhagsPa", "Microsoft Tai Le", "Microsoft Uighur", "Microsoft YaHei", "Microsoft Yi Baiti", "MingLiU", "MingLiU_HKSCS", "MingLiU_HKSCS-ExtB", "MingLiU-ExtB", "Minion", "Minion Pro", "Miriam", "Miriam Fixed", "Mistral", "Modern", "Modern No. 20", "Mona Lisa Solid ITC TT", "Mongolian Baiti", "MONO", "MoolBoran", "Mrs Eaves", "MS LineDraw", "MS Mincho", "MS PMincho", "MS Reference Specialty", "MS UI Gothic", "MT Extra", "MUSEO", "MV Boli", "Nadeem", "Narkisim", "NEVIS", "News Gothic", "News GothicMT", "NewsGoth BT", "Niagara Engraved", "Niagara Solid", "Noteworthy", "NSimSun", "Nyala", "OCR A Extended", "Old Century", "Old English Text MT", "Onyx", "Onyx BT", "OPTIMA", "Oriya Sangam MN", "OSAKA", "OzHandicraft BT", "Palace Script MT", "Papyrus", "Parchment", "Party LET", "Pegasus", "Perpetua", "Perpetua Titling MT", "PetitaBold", "Pickwick", "Plantagenet Cherokee", "Playbill", "PMingLiU", "PMingLiU-ExtB", "Poor Richard", "Poster", "PosterBodoni BT", "PRINCETOWN LET", "Pristina", "PTBarnum BT", "Pythagoras", "Raavi", "Rage Italic", "Ravie", "Ribbon131 Bd BT", "Rockwell", "Rockwell Condensed", "Rockwell Extra Bold", "Rod", "Roman", "Sakkal Majalla", "Santa Fe LET", "Savoye LET", "Sceptre", "Script", "Script MT Bold", "SCRIPTINA", "Serifa", "Serifa BT", "Serifa Th BT", "ShelleyVolante BT", "Sherwood", "Shonar Bangla", "Showcard Gothic", "Shruti", "Signboard", "SILKSCREEN", "SimHei", "Simplified Arabic", "Simplified Arabic Fixed", "SimSun", "SimSun-ExtB", "Sinhala Sangam MN", "Sketch Rockwell", "Skia", "Small Fonts", "Snap ITC", "Snell Roundhand", "Socket", "Souvenir Lt BT", "Staccato222 BT", "Steamer", "Stencil", "Storybook", "Styllo", "Subway", "Swis721 BlkEx BT", "Swiss911 XCm BT", "Sylfaen", "Synchro LET", "System", "Tamil Sangam MN", "Technical", "Teletype", "Telugu Sangam MN", "Tempus Sans ITC", "Terminal", "Thonburi", "Traditional Arabic", "Trajan", "TRAJAN PRO", "Tristan", "Tubular", "Tunga", "Tw Cen MT", "Tw Cen MT Condensed", "Tw Cen MT Condensed Extra Bold", "TypoUpright BT", "Unicorn", "Univers", "Univers CE 55 Medium", "Univers Condensed", "Utsaah", "Vagabond", "Vani", "Vijaya", "Viner Hand ITC", "VisualUI", "Vivaldi", "Vladimir Script", "Vrinda", "Westminster", "WHITNEY", "Wide Latin", "ZapfEllipt BT", "ZapfHumnst BT", "ZapfHumnst Dm BT", "Zapfino", "Zurich BlkEx BT", "Zurich Ex BT", "ZWAdobeF"];
            if (that.options.extendedJsFonts) {
                fontList = fontList.concat(extendedFontList)
            }
            fontList = fontList.concat(that.options.userDefinedFonts);
            var testString = "mmmmmmmmmmlli";
            var testSize = "72px";
            var h = document.getElementsByTagName("body")[0];
            var baseFontsDiv = document.createElement("div");
            var fontsDiv = document.createElement("div");
            var defaultWidth = {};
            var defaultHeight = {};
            var createSpan = function () {
                var s = document.createElement("span");
                s.style.position = "absolute";
                s.style.left = "-9999px";
                s.style.fontSize = testSize;
                s.style.lineHeight = "normal";
                s.innerHTML = testString;
                return s
            };
            var createSpanWithFonts = function (fontToDetect, baseFont) {
                var s = createSpan();
                s.style.fontFamily = "'" + fontToDetect + "'," + baseFont;
                return s
            };
            var initializeBaseFontsSpans = function () {
                var spans = [];
                for (var index = 0, length = baseFonts.length; index < length; index++) {
                    var s = createSpan();
                    s.style.fontFamily = baseFonts[index];
                    baseFontsDiv.appendChild(s);
                    spans.push(s)
                }
                return spans
            };
            var initializeFontsSpans = function () {
                var spans = {};
                for (var i = 0, l = fontList.length; i < l; i++) {
                    var fontSpans = [];
                    for (var j = 0, numDefaultFonts = baseFonts.length; j < numDefaultFonts; j++) {
                        var s = createSpanWithFonts(fontList[i], baseFonts[j]);
                        fontsDiv.appendChild(s);
                        fontSpans.push(s)
                    }
                    spans[fontList[i]] = fontSpans
                }
                return spans
            };
            var isFontAvailable = function (fontSpans) {
                var detected = false;
                for (var i = 0; i < baseFonts.length; i++) {
                    detected = fontSpans[i].offsetWidth !== defaultWidth[baseFonts[i]] || fontSpans[i].offsetHeight !== defaultHeight[baseFonts[i]];
                    if (detected) {
                        return detected
                    }
                }
                return detected
            };
            var baseFontsSpans = initializeBaseFontsSpans();
            h.appendChild(baseFontsDiv);
            for (var index = 0, length = baseFonts.length; index < length; index++) {
                defaultWidth[baseFonts[index]] = baseFontsSpans[index].offsetWidth;
                defaultHeight[baseFonts[index]] = baseFontsSpans[index].offsetHeight
            }
            var fontsSpans = initializeFontsSpans();
            h.appendChild(fontsDiv);
            var available = [];
            for (var i = 0, l = fontList.length; i < l; i++) {
                if (isFontAvailable(fontsSpans[fontList[i]])) {
                    available.push(fontList[i])
                }
            }
            h.removeChild(fontsDiv);
            h.removeChild(baseFontsDiv);
            keys.push({
                key: "js_fonts",
                value: available
            });
            done(keys)
        }, 1)
    },
    pluginsKey: function (keys) {
        var plugins;
        if (!this.options.excludePlugins) {
            if (this.isIE()) {
                if (!this.options.excludeIEPlugins) {
                    plugins = this.getIEPlugins()
                }
            } else {
                plugins = this.getRegularPlugins()
            }
        }
        return plugins.length
    },
    getRegularPlugins: function () {
        var plugins = [];
        for (var i = 0, l = navigator.plugins.length; i < l; i++) {
            plugins.push(navigator.plugins[i])
        }
        if (this.pluginsShouldBeSorted()) {
            plugins = plugins.sort(function (a, b) {
                if (a.name > b.name) {
                    return 1
                }
                if (a.name < b.name) {
                    return -1
                }
                return 0
            })
        }
        return this.map(plugins, function (p) {
            var mimeTypes = this.map(p, function (mt) {
                return [mt.type, mt.suffixes].join("~")
            }).join(",");
            return [p.name, p.description, mimeTypes].join("::")
        }, this)
    },
    getIEPlugins: function () {
        var result = [];
        if (Object.getOwnPropertyDescriptor && Object.getOwnPropertyDescriptor(window, "ActiveXObject") || "ActiveXObject" in window) {
            var names = ["AcroPDF.PDF", "Adodb.Stream", "AgControl.AgControl", "DevalVRXCtrl.DevalVRXCtrl.1", "MacromediaFlashPaper.MacromediaFlashPaper", "Msxml2.DOMDocument", "Msxml2.XMLHTTP", "PDF.PdfCtrl", "QuickTime.QuickTime", "QuickTimeCheckObject.QuickTimeCheck.1", "RealPlayer", "RealPlayer.RealPlayer(tm) ActiveX Control (32-bit)", "RealVideo.RealVideo(tm) ActiveX Control (32-bit)", "Scripting.Dictionary", "SWCtl.SWCtl", "Shell.UIHelper", "ShockwaveFlash.ShockwaveFlash", "Skype.Detection", "TDCCtl.TDCCtl", "WMPlayer.OCX", "rmocx.RealPlayer G2 Control", "rmocx.RealPlayer G2 Control.1"];
            result = this.map(names, function (name) {
                try {
                    new ActiveXObject(name);
                    return name
                } catch (e) {
                    return null
                }
            })
        }
        if (navigator.plugins) {
            result = result.concat(this.getRegularPlugins())
        }
        return result
    },
    pluginsShouldBeSorted: function () {
        var should = false;
        for (var i = 0, l = this.options.sortPluginsFor.length; i < l; i++) {
            var re = this.options.sortPluginsFor[i];
            if (navigator.userAgent.match(re)) {
                should = true;
                break
            }
        }
        return should
    },
    touchSupportKey: function (keys) {
        var touchSupportKey;
        if (!this.options.excludeTouchSupport) {
            touchSupportKey = this.getTouchSupport()
        }
        return touchSupportKey
    },
    hardwareConcurrencyKey: function (keys) {
        var hardware_concurrency;
        if (!this.options.excludeHardwareConcurrency) {
            hardware_concurrency = this.getHardwareConcurrency()
        }
        return hardware_concurrency
    },
    hasSessionStorage: function () {
        try {
            return !!window.sessionStorage
        } catch (e) {
            return true
        }
    },
    hasLocalStorage: function () {
        try {
            return !!window.localStorage
        } catch (e) {
            return true
        }
    },
    hasIndexedDB: function () {
        try {
            return !!window.indexedDB
        } catch (e) {
            return true
        }
    },
    getHardwareConcurrency: function () {
        if (navigator.hardwareConcurrency) {
            return navigator.hardwareConcurrency
        }
        return "unknown"
    },
    getNavigatorCpuClass: function () {
        if (navigator.cpuClass) {
            return navigator.cpuClass
        } else {
            return "unknown"
        }
    },
    getNavigatorPlatform: function () {
        if (navigator.platform) {
            return navigator.platform
        } else {
            return "unknown"
        }
    },
    getDoNotTrack: function () {
        if (navigator.doNotTrack) {
            return navigator.doNotTrack
        } else if (navigator.msDoNotTrack) {
            return navigator.msDoNotTrack
        } else if (window.doNotTrack) {
            return window.doNotTrack
        } else {
            return "unknown"
        }
    },
    getTouchSupport: function () {
        var maxTouchPoints = 0;
        var touchEvent = false;
        if (typeof navigator.maxTouchPoints !== "undefined") {
            maxTouchPoints = navigator.maxTouchPoints
        } else if (typeof navigator.msMaxTouchPoints !== "undefined") {
            maxTouchPoints = navigator.msMaxTouchPoints
        }
        try {
            document.createEvent("TouchEvent");
            touchEvent = true
        } catch (_) {
        }
        var touchStart = "ontouchstart" in window;
        return maxTouchPoints + "_" + touchEvent + "_" + touchStart
    },
    getCanvasFp: function () {
        var result = [];
        var canvas = document.createElement("canvas");
        canvas.width = 2e3;
        canvas.height = 200;
        canvas.style.display = "inline";
        var ctx = canvas.getContext("2d");
        ctx.rect(0, 0, 10, 10);
        ctx.rect(2, 2, 6, 6);
        result.push("canvas winding:" + (ctx.isPointInPath(5, 5, "evenodd") === false ? "yes" : "no"));
        ctx.textBaseline = "alphabetic";
        ctx.fillStyle = "#f60";
        ctx.fillRect(125, 1, 62, 20);
        ctx.fillStyle = "#069";
        if (this.options.dontUseFakeFontInCanvas) {
            ctx.font = "11pt Arial"
        } else {
            ctx.font = "11pt no-real-font-123"
        }
        ctx.fillText("Cwm fjordbank glyphs vext quiz, 😃", 2, 15);
        ctx.fillStyle = "rgba(102, 204, 0, 0.2)";
        ctx.font = "18pt Arial";
        ctx.fillText("Cwm fjordbank glyphs vext quiz, 😃", 4, 45);
        ctx.globalCompositeOperation = "multiply";
        ctx.fillStyle = "rgb(255,0,255)";
        ctx.beginPath();
        ctx.arc(50, 50, 50, 0, Math.PI * 2, true);
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = "rgb(0,255,255)";
        ctx.beginPath();
        ctx.arc(100, 50, 50, 0, Math.PI * 2, true);
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = "rgb(255,255,0)";
        ctx.beginPath();
        ctx.arc(75, 100, 50, 0, Math.PI * 2, true);
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = "rgb(255,0,255)";
        ctx.arc(75, 75, 75, 0, Math.PI * 2, true);
        ctx.arc(75, 75, 25, 0, Math.PI * 2, true);
        ctx.fill("evenodd");
        result.push("canvas fp:" + canvas.toDataURL());
        return result.join("~")
    },
    getWebglFp: function () {
        var gl;
        var fa2s = function (fa) {
            gl.clearColor(0, 0, 0, 1);
            gl.enable(gl.DEPTH_TEST);
            gl.depthFunc(gl.LEQUAL);
            gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
            return "[" + fa[0] + ", " + fa[1] + "]"
        };
        var maxAnisotropy = function (gl) {
            var anisotropy,
                ext = gl.getExtension("EXT_texture_filter_anisotropic") || gl.getExtension("WEBKIT_EXT_texture_filter_anisotropic") || gl.getExtension("MOZ_EXT_texture_filter_anisotropic");
            return ext ? (anisotropy = gl.getParameter(ext.MAX_TEXTURE_MAX_ANISOTROPY_EXT),
            0 === anisotropy && (anisotropy = 2),
                anisotropy) : null
        };
        gl = this.getWebglCanvas();
        if (!gl) {
            return null
        }
        var result = [];
        var vShaderTemplate = "attribute vec2 attrVertex;varying vec2 varyinTexCoordinate;uniform vec2 uniformOffset;void main(){varyinTexCoordinate=attrVertex+uniformOffset;gl_Position=vec4(attrVertex,0,1);}";
        var fShaderTemplate = "precision mediump float;varying vec2 varyinTexCoordinate;void main() {gl_FragColor=vec4(varyinTexCoordinate,0,1);}";
        var vertexPosBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, vertexPosBuffer);
        var vertices = new Float32Array([-.2, -.9, 0, .4, -.26, 0, 0, .732134444, 0]);
        gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
        vertexPosBuffer.itemSize = 3;
        vertexPosBuffer.numItems = 3;
        var program = gl.createProgram()
            , vshader = gl.createShader(gl.VERTEX_SHADER);
        gl.shaderSource(vshader, vShaderTemplate);
        gl.compileShader(vshader);
        var fshader = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(fshader, fShaderTemplate);
        gl.compileShader(fshader);
        gl.attachShader(program, vshader);
        gl.attachShader(program, fshader);
        gl.linkProgram(program);
        gl.useProgram(program);
        program.vertexPosAttrib = gl.getAttribLocation(program, "attrVertex");
        program.offsetUniform = gl.getUniformLocation(program, "uniformOffset");
        gl.enableVertexAttribArray(program.vertexPosArray);
        gl.vertexAttribPointer(program.vertexPosAttrib, vertexPosBuffer.itemSize, gl.FLOAT, !1, 0, 0);
        gl.uniform2f(program.offsetUniform, 1, 1);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, vertexPosBuffer.numItems);
        if (gl.canvas != null) {
            result.push(gl.canvas.toDataURL())
        }
        result.push("extensions:" + gl.getSupportedExtensions().join(";"));
        result.push("webgl aliased line width range:" + fa2s(gl.getParameter(gl.ALIASED_LINE_WIDTH_RANGE)));
        result.push("webgl aliased point size range:" + fa2s(gl.getParameter(gl.ALIASED_POINT_SIZE_RANGE)));
        result.push("webgl alpha bits:" + gl.getParameter(gl.ALPHA_BITS));
        result.push("webgl antialiasing:" + (gl.getContextAttributes().antialias ? "yes" : "no"));
        result.push("webgl blue bits:" + gl.getParameter(gl.BLUE_BITS));
        result.push("webgl depth bits:" + gl.getParameter(gl.DEPTH_BITS));
        result.push("webgl green bits:" + gl.getParameter(gl.GREEN_BITS));
        result.push("webgl max anisotropy:" + maxAnisotropy(gl));
        result.push("webgl max combined texture image units:" + gl.getParameter(gl.MAX_COMBINED_TEXTURE_IMAGE_UNITS));
        result.push("webgl max cube map texture size:" + gl.getParameter(gl.MAX_CUBE_MAP_TEXTURE_SIZE));
        result.push("webgl max fragment uniform vectors:" + gl.getParameter(gl.MAX_FRAGMENT_UNIFORM_VECTORS));
        result.push("webgl max render buffer size:" + gl.getParameter(gl.MAX_RENDERBUFFER_SIZE));
        result.push("webgl max texture image units:" + gl.getParameter(gl.MAX_TEXTURE_IMAGE_UNITS));
        result.push("webgl max texture size:" + gl.getParameter(gl.MAX_TEXTURE_SIZE));
        result.push("webgl max varying vectors:" + gl.getParameter(gl.MAX_VARYING_VECTORS));
        result.push("webgl max vertex attribs:" + gl.getParameter(gl.MAX_VERTEX_ATTRIBS));
        result.push("webgl max vertex texture image units:" + gl.getParameter(gl.MAX_VERTEX_TEXTURE_IMAGE_UNITS));
        result.push("webgl max vertex uniform vectors:" + gl.getParameter(gl.MAX_VERTEX_UNIFORM_VECTORS));
        result.push("webgl max viewport dims:" + fa2s(gl.getParameter(gl.MAX_VIEWPORT_DIMS)));
        result.push("webgl red bits:" + gl.getParameter(gl.RED_BITS));
        result.push("webgl renderer:" + gl.getParameter(gl.RENDERER));
        result.push("webgl shading language version:" + gl.getParameter(gl.SHADING_LANGUAGE_VERSION));
        result.push("webgl stencil bits:" + gl.getParameter(gl.STENCIL_BITS));
        result.push("webgl vendor:" + gl.getParameter(gl.VENDOR));
        result.push("webgl version:" + gl.getParameter(gl.VERSION));
        try {
            var extensionDebugRendererInfo = gl.getExtension("WEBGL_debug_renderer_info");
            if (!extensionDebugRendererInfo) {
                if (typeof NODEBUG === "undefined") {
                    this.log("WebGL fingerprinting is incomplete, because your browser does not have the extension WEBGL_debug_renderer_info")
                }
            } else {
                result.push("webgl unmasked vendor:" + gl.getParameter(extensionDebugRendererInfo.UNMASKED_VENDOR_WEBGL));
                result.push("webgl unmasked renderer:" + gl.getParameter(extensionDebugRendererInfo.UNMASKED_RENDERER_WEBGL))
            }
        } catch (e) {
        }
        if (!gl.getShaderPrecisionFormat) {
            if (typeof NODEBUG === "undefined") {
                this.log("WebGL fingerprinting is incomplete, because your browser does not support getShaderPrecisionFormat")
            }
            return result.join("~")
        }
        result.push("webgl vertex shader high float precision:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_FLOAT).precision);
        result.push("webgl vertex shader high float precision rangeMin:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_FLOAT).rangeMin);
        result.push("webgl vertex shader high float precision rangeMax:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_FLOAT).rangeMax);
        result.push("webgl vertex shader medium float precision:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_FLOAT).precision);
        result.push("webgl vertex shader medium float precision rangeMin:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_FLOAT).rangeMin);
        result.push("webgl vertex shader medium float precision rangeMax:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_FLOAT).rangeMax);
        result.push("webgl vertex shader low float precision:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_FLOAT).precision);
        result.push("webgl vertex shader low float precision rangeMin:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_FLOAT).rangeMin);
        result.push("webgl vertex shader low float precision rangeMax:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_FLOAT).rangeMax);
        result.push("webgl fragment shader high float precision:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_FLOAT).precision);
        result.push("webgl fragment shader high float precision rangeMin:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_FLOAT).rangeMin);
        result.push("webgl fragment shader high float precision rangeMax:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_FLOAT).rangeMax);
        result.push("webgl fragment shader medium float precision:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_FLOAT).precision);
        result.push("webgl fragment shader medium float precision rangeMin:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_FLOAT).rangeMin);
        result.push("webgl fragment shader medium float precision rangeMax:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_FLOAT).rangeMax);
        result.push("webgl fragment shader low float precision:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_FLOAT).precision);
        result.push("webgl fragment shader low float precision rangeMin:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_FLOAT).rangeMin);
        result.push("webgl fragment shader low float precision rangeMax:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_FLOAT).rangeMax);
        result.push("webgl vertex shader high int precision:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_INT).precision);
        result.push("webgl vertex shader high int precision rangeMin:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_INT).rangeMin);
        result.push("webgl vertex shader high int precision rangeMax:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.HIGH_INT).rangeMax);
        result.push("webgl vertex shader medium int precision:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_INT).precision);
        result.push("webgl vertex shader medium int precision rangeMin:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_INT).rangeMin);
        result.push("webgl vertex shader medium int precision rangeMax:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.MEDIUM_INT).rangeMax);
        result.push("webgl vertex shader low int precision:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_INT).precision);
        result.push("webgl vertex shader low int precision rangeMin:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_INT).rangeMin);
        result.push("webgl vertex shader low int precision rangeMax:" + gl.getShaderPrecisionFormat(gl.VERTEX_SHADER, gl.LOW_INT).rangeMax);
        result.push("webgl fragment shader high int precision:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_INT).precision);
        result.push("webgl fragment shader high int precision rangeMin:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_INT).rangeMin);
        result.push("webgl fragment shader high int precision rangeMax:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_INT).rangeMax);
        result.push("webgl fragment shader medium int precision:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_INT).precision);
        result.push("webgl fragment shader medium int precision rangeMin:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_INT).rangeMin);
        result.push("webgl fragment shader medium int precision rangeMax:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_INT).rangeMax);
        result.push("webgl fragment shader low int precision:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_INT).precision);
        result.push("webgl fragment shader low int precision rangeMin:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_INT).rangeMin);
        result.push("webgl fragment shader low int precision rangeMax:" + gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.LOW_INT).rangeMax);
        return result.join("~")
    },
    getAdBlock: function () {
        var ads = document.createElement("div");
        ads.innerHTML = "&nbsp;";
        ads.className = "adsbox";
        var result = false;
        try {
            document.body.appendChild(ads);
            result = document.getElementsByClassName("adsbox")[0].offsetHeight === 0;
            document.body.removeChild(ads)
        } catch (e) {
            result = false
        }
        return result
    },
    getHasLiedLanguages: function () {
        if (typeof navigator.languages !== "undefined") {
            try {
                var firstLanguages = navigator.languages[0].substr(0, 2);
                if (firstLanguages !== navigator.language.substr(0, 2)) {
                    return true
                }
            } catch (err) {
                return true
            }
        }
        return false
    },
    getHasLiedResolution: function () {
        if (screen.width < screen.availWidth) {
            return true
        }
        if (screen.height < screen.availHeight) {
            return true
        }
        return false
    },
    getHasLiedOs: function () {
        var userAgent = navigator.userAgent.toLowerCase();
        var oscpu = navigator.oscpu;
        var platform = navigator.platform.toLowerCase();
        var os;
        if (userAgent.indexOf("windows phone") >= 0) {
            os = "Windows Phone"
        } else if (userAgent.indexOf("win") >= 0) {
            os = "Windows"
        } else if (userAgent.indexOf("android") >= 0) {
            os = "Android"
        } else if (userAgent.indexOf("linux") >= 0) {
            os = "Linux"
        } else if (userAgent.indexOf("iphone") >= 0 || userAgent.indexOf("ipad") >= 0) {
            os = "iOS"
        } else if (userAgent.indexOf("mac") >= 0) {
            os = "Mac"
        } else {
            os = "Other"
        }
        var mobileDevice;
        if ("ontouchstart" in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0) {
            mobileDevice = true
        } else {
            mobileDevice = false
        }
        if (mobileDevice && os !== "Windows Phone" && os !== "Android" && os !== "iOS" && os !== "Other") {
            return true
        }
        if (typeof oscpu !== "undefined") {
            oscpu = oscpu.toLowerCase();
            if (oscpu.indexOf("win") >= 0 && os !== "Windows" && os !== "Windows Phone") {
                return true
            } else if (oscpu.indexOf("linux") >= 0 && os !== "Linux" && os !== "Android") {
                return true
            } else if (oscpu.indexOf("mac") >= 0 && os !== "Mac" && os !== "iOS") {
                return true
            } else if (oscpu.indexOf("win") === 0 && oscpu.indexOf("linux") === 0 && oscpu.indexOf("mac") >= 0 && os !== "other") {
                return true
            }
        }
        if (platform.indexOf("win") >= 0 && os !== "Windows" && os !== "Windows Phone") {
            return true
        } else if ((platform.indexOf("linux") >= 0 || platform.indexOf("android") >= 0 || platform.indexOf("pike") >= 0) && os !== "Linux" && os !== "Android") {
            return true
        } else if ((platform.indexOf("mac") >= 0 || platform.indexOf("ipad") >= 0 || platform.indexOf("ipod") >= 0 || platform.indexOf("iphone") >= 0) && os !== "Mac" && os !== "iOS") {
            return true
        } else if (platform.indexOf("win") === 0 && platform.indexOf("linux") === 0 && platform.indexOf("mac") >= 0 && os !== "other") {
            return true
        }
        if (typeof navigator.plugins === "undefined" && os !== "Windows" && os !== "Windows Phone") {
            return true
        }
        return false
    },
    getHasLiedBrowser: function () {
        var userAgent = navigator.userAgent.toLowerCase();
        var productSub = navigator.productSub;
        var browser;
        if (userAgent.indexOf("firefox") >= 0) {
            browser = "Firefox"
        } else if (userAgent.indexOf("opera") >= 0 || userAgent.indexOf("opr") >= 0) {
            browser = "Opera"
        } else if (userAgent.indexOf("chrome") >= 0) {
            browser = "Chrome"
        } else if (userAgent.indexOf("safari") >= 0) {
            browser = "Safari"
        } else if (userAgent.indexOf("trident") >= 0) {
            browser = "Internet Explorer"
        } else {
            browser = "Other"
        }
        if ((browser === "Chrome" || browser === "Safari" || browser === "Opera") && productSub !== "20030107") {
            return true
        }
        var tempRes = eval.toString().length;
        if (tempRes === 37 && browser !== "Safari" && browser !== "Firefox" && browser !== "Other") {
            return true
        } else if (tempRes === 39 && browser !== "Internet Explorer" && browser !== "Other") {
            return true
        } else if (tempRes === 33 && browser !== "Chrome" && browser !== "Opera" && browser !== "Other") {
            return true
        }
        var errFirefox;
        try {
            throw "a"
        } catch (err) {
            try {
                err.toSource();
                errFirefox = true
            } catch (errOfErr) {
                errFirefox = false
            }
        }
        if (errFirefox && browser !== "Firefox" && browser !== "Other") {
            return true
        }
        return false
    },
    isCanvasSupported: function () {
        var elem = document.createElement("canvas");
        return !!(elem.getContext && elem.getContext("2d"))
    },
    isWebGlSupported: function () {
        if (!this.isCanvasSupported()) {
            return false
        }
        var canvas = document.createElement("canvas"), glContext;
        try {
            glContext = canvas.getContext && (canvas.getContext("webgl") || canvas.getContext("experimental-webgl"))
        } catch (e) {
            glContext = false
        }
        return !!window.WebGLRenderingContext && !!glContext
    },
    isIE: function () {
        if (navigator.appName === "Microsoft Internet Explorer") {
            return true
        } else if (navigator.appName === "Netscape" && /Trident/.test(navigator.userAgent)) {
            return true
        }
        return false
    },
    hasSwfObjectLoaded: function () {
        return typeof window.swfobject !== "undefined"
    },
    hasMinFlashInstalled: function () {
        return swfobject.hasFlashPlayerVersion("9.0.0")
    },
    addFlashDivNode: function () {
        var node = document.createElement("div");
        node.setAttribute("id", this.options.swfContainerId);
        document.body.appendChild(node)
    },
    loadSwfAndDetectFonts: function (done) {
        var hiddenCallback = "___fp_swf_loaded";
        window[hiddenCallback] = function (fonts) {
            done(fonts)
        }
        ;
        var id = this.options.swfContainerId;
        this.addFlashDivNode();
        var flashvars = {
            onReady: hiddenCallback
        };
        var flashparams = {
            allowScriptAccess: "always",
            menu: "false"
        };
        swfobject.embedSWF(this.options.swfPath, id, "1", "1", "9.0.0", false, flashvars, flashparams, {})
    },
    getWebglCanvas: function () {
        var canvas = document.createElement("canvas");
        var gl = null;
        try {
            gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl")
        } catch (e) {
        }
        if (!gl) {
            gl = null
        }
        return gl
    },
    each: function (obj, iterator, context) {
        if (obj === null) {
            return
        }
        if (this.nativeForEach && obj.forEach === this.nativeForEach) {
            obj.forEach(iterator, context)
        } else if (obj.length === +obj.length) {
            for (var i = 0, l = obj.length; i < l; i++) {
                if (iterator.call(context, obj[i], i, obj) === {}) {
                    return
                }
            }
        } else {
            for (var key in obj) {
                if (obj.hasOwnProperty(key)) {
                    if (iterator.call(context, obj[key], key, obj) === {}) {
                        return
                    }
                }
            }
        }
    },
    map: function (obj, iterator, context) {
        var results = [];
        if (obj == null) {
            return results
        }
        if (this.nativeMap && obj.map === this.nativeMap) {
            return obj.map(iterator, context)
        }
        this.each(obj, function (value, index, list) {
            results[results.length] = iterator.call(context, value, index, list)
        });
        return results
    },
    x64Add: function (m, n) {
        m = [m[0] >>> 16, m[0] & 65535, m[1] >>> 16, m[1] & 65535];
        n = [n[0] >>> 16, n[0] & 65535, n[1] >>> 16, n[1] & 65535];
        var o = [0, 0, 0, 0];
        o[3] += m[3] + n[3];
        o[2] += o[3] >>> 16;
        o[3] &= 65535;
        o[2] += m[2] + n[2];
        o[1] += o[2] >>> 16;
        o[2] &= 65535;
        o[1] += m[1] + n[1];
        o[0] += o[1] >>> 16;
        o[1] &= 65535;
        o[0] += m[0] + n[0];
        o[0] &= 65535;
        return [o[0] << 16 | o[1], o[2] << 16 | o[3]]
    },
    x64Multiply: function (m, n) {
        m = [m[0] >>> 16, m[0] & 65535, m[1] >>> 16, m[1] & 65535];
        n = [n[0] >>> 16, n[0] & 65535, n[1] >>> 16, n[1] & 65535];
        var o = [0, 0, 0, 0];
        o[3] += m[3] * n[3];
        o[2] += o[3] >>> 16;
        o[3] &= 65535;
        o[2] += m[2] * n[3];
        o[1] += o[2] >>> 16;
        o[2] &= 65535;
        o[2] += m[3] * n[2];
        o[1] += o[2] >>> 16;
        o[2] &= 65535;
        o[1] += m[1] * n[3];
        o[0] += o[1] >>> 16;
        o[1] &= 65535;
        o[1] += m[2] * n[2];
        o[0] += o[1] >>> 16;
        o[1] &= 65535;
        o[1] += m[3] * n[1];
        o[0] += o[1] >>> 16;
        o[1] &= 65535;
        o[0] += m[0] * n[3] + m[1] * n[2] + m[2] * n[1] + m[3] * n[0];
        o[0] &= 65535;
        return [o[0] << 16 | o[1], o[2] << 16 | o[3]]
    },
    x64Rotl: function (m, n) {
        n %= 64;
        if (n === 32) {
            return [m[1], m[0]]
        } else if (n < 32) {
            return [m[0] << n | m[1] >>> 32 - n, m[1] << n | m[0] >>> 32 - n]
        } else {
            n -= 32;
            return [m[1] << n | m[0] >>> 32 - n, m[0] << n | m[1] >>> 32 - n]
        }
    },
    x64LeftShift: function (m, n) {
        n %= 64;
        if (n === 0) {
            return m
        } else if (n < 32) {
            return [m[0] << n | m[1] >>> 32 - n, m[1] << n]
        } else {
            return [m[1] << n - 32, 0]
        }
    },
    x64Xor: function (m, n) {
        return [m[0] ^ n[0], m[1] ^ n[1]]
    },
    x64Fmix: function (h) {
        h = this.x64Xor(h, [0, h[0] >>> 1]);
        h = this.x64Multiply(h, [4283543511, 3981806797]);
        h = this.x64Xor(h, [0, h[0] >>> 1]);
        h = this.x64Multiply(h, [3301882366, 444984403]);
        h = this.x64Xor(h, [0, h[0] >>> 1]);
        return h
    },
    x64hash128: function (key, seed) {
        key = key || "";
        seed = seed || 0;
        var remainder = key.length % 16;
        var bytes = key.length - remainder;
        var h1 = [0, seed];
        var h2 = [0, seed];
        var k1 = [0, 0];
        var k2 = [0, 0];
        var c1 = [2277735313, 289559509];
        var c2 = [1291169091, 658871167];
        for (var i = 0; i < bytes; i = i + 16) {
            k1 = [key.charCodeAt(i + 4) & 255 | (key.charCodeAt(i + 5) & 255) << 8 | (key.charCodeAt(i + 6) & 255) << 16 | (key.charCodeAt(i + 7) & 255) << 24, key.charCodeAt(i) & 255 | (key.charCodeAt(i + 1) & 255) << 8 | (key.charCodeAt(i + 2) & 255) << 16 | (key.charCodeAt(i + 3) & 255) << 24];
            k2 = [key.charCodeAt(i + 12) & 255 | (key.charCodeAt(i + 13) & 255) << 8 | (key.charCodeAt(i + 14) & 255) << 16 | (key.charCodeAt(i + 15) & 255) << 24, key.charCodeAt(i + 8) & 255 | (key.charCodeAt(i + 9) & 255) << 8 | (key.charCodeAt(i + 10) & 255) << 16 | (key.charCodeAt(i + 11) & 255) << 24];
            k1 = this.x64Multiply(k1, c1);
            k1 = this.x64Rotl(k1, 31);
            k1 = this.x64Multiply(k1, c2);
            h1 = this.x64Xor(h1, k1);
            h1 = this.x64Rotl(h1, 27);
            h1 = this.x64Add(h1, h2);
            h1 = this.x64Add(this.x64Multiply(h1, [0, 5]), [0, 1390208809]);
            k2 = this.x64Multiply(k2, c2);
            k2 = this.x64Rotl(k2, 33);
            k2 = this.x64Multiply(k2, c1);
            h2 = this.x64Xor(h2, k2);
            h2 = this.x64Rotl(h2, 31);
            h2 = this.x64Add(h2, h1);
            h2 = this.x64Add(this.x64Multiply(h2, [0, 5]), [0, 944331445])
        }
        k1 = [0, 0];
        k2 = [0, 0];
        switch (remainder) {
            case 15:
                k2 = this.x64Xor(k2, this.x64LeftShift([0, key.charCodeAt(i + 14)], 48));
            case 14:
                k2 = this.x64Xor(k2, this.x64LeftShift([0, key.charCodeAt(i + 13)], 40));
            case 13:
                k2 = this.x64Xor(k2, this.x64LeftShift([0, key.charCodeAt(i + 12)], 32));
            case 12:
                k2 = this.x64Xor(k2, this.x64LeftShift([0, key.charCodeAt(i + 11)], 24));
            case 11:
                k2 = this.x64Xor(k2, this.x64LeftShift([0, key.charCodeAt(i + 10)], 16));
            case 10:
                k2 = this.x64Xor(k2, this.x64LeftShift([0, key.charCodeAt(i + 9)], 8));
            case 9:
                k2 = this.x64Xor(k2, [0, key.charCodeAt(i + 8)]);
                k2 = this.x64Multiply(k2, c2);
                k2 = this.x64Rotl(k2, 33);
                k2 = this.x64Multiply(k2, c1);
                h2 = this.x64Xor(h2, k2);
            case 8:
                k1 = this.x64Xor(k1, this.x64LeftShift([0, key.charCodeAt(i + 7)], 56));
            case 7:
                k1 = this.x64Xor(k1, this.x64LeftShift([0, key.charCodeAt(i + 6)], 48));
            case 6:
                k1 = this.x64Xor(k1, this.x64LeftShift([0, key.charCodeAt(i + 5)], 40));
            case 5:
                k1 = this.x64Xor(k1, this.x64LeftShift([0, key.charCodeAt(i + 4)], 32));
            case 4:
                k1 = this.x64Xor(k1, this.x64LeftShift([0, key.charCodeAt(i + 3)], 24));
            case 3:
                k1 = this.x64Xor(k1, this.x64LeftShift([0, key.charCodeAt(i + 2)], 16));
            case 2:
                k1 = this.x64Xor(k1, this.x64LeftShift([0, key.charCodeAt(i + 1)], 8));
            case 1:
                k1 = this.x64Xor(k1, [0, key.charCodeAt(i)]);
                k1 = this.x64Multiply(k1, c1);
                k1 = this.x64Rotl(k1, 31);
                k1 = this.x64Multiply(k1, c2);
                h1 = this.x64Xor(h1, k1)
        }
        h1 = this.x64Xor(h1, [0, key.length]);
        h2 = this.x64Xor(h2, [0, key.length]);
        h1 = this.x64Add(h1, h2);
        h2 = this.x64Add(h2, h1);
        h1 = this.x64Fmix(h1);
        h2 = this.x64Fmix(h2);
        h1 = this.x64Add(h1, h2);
        h2 = this.x64Add(h2, h1);
        return ("00000000" + (h1[0] >>> 0).toString(16)).slice(-8) + ("00000000" + (h1[1] >>> 0).toString(16)).slice(-8) + ("00000000" + (h2[0] >>> 0).toString(16)).slice(-8) + ("00000000" + (h2[1] >>> 0).toString(16)).slice(-8)
    }
};
Fingerprint2.VERSION = "1.5.0";

function createFinger2() {
    var fp = new Fingerprint2;
    return fp.get()
}
console.log(createFinger2());