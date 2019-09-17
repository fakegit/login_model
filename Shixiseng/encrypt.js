function myencode(source){
    var nstr = [];
    var key=[23,24,39,38,22,11,13,63];
    var s;
    var str = source.slice(0).split("");
    while ( str.length ) {
       s = str.shift();
       nstr.push( String( s.charCodeAt() ).split("").reverse().join("") );
    }
    nstr = nstr.reverse().join('X');

    return nstr;
}


