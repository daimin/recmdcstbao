/**
 *
 * Created by daimin on 15/4/9.
 */
var Class = {
    create: function() { return function() { this.init.apply(this, arguments);}}
}
var MMMask = Class.create();

MMMask.prototype = {
	init : function(){},
    add : function(){
    	var newMask = document.createElement("div");
        newMask.id = "__mask";
        newMask.style.position = "absolute";
        newMask.style.zIndex = "1";
        _scrollWidth = Math.max(document.body.scrollWidth, document.documentElement.scrollWidth);
        _scrollHeight = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
        newMask.style.width = _scrollWidth + "px";
        newMask.style.height = _scrollHeight + "px";
        newMask.style.top = "0px";
        newMask.style.left = "0px";
        newMask.style.background = "#bbb";
        newMask.style.filter = "alpha(opacity=30)";
        newMask.style.opacity = "0.30";
        newMask.style.textAlign = "center";
        newMask.innerHTML = '<div style="color:red;font-size:24px;font-weight:bold;margin-top:' + ((_scrollHeight - 128) / 2 ) + 'px"><img src="/static/images/loading.gif"></div>';
        document.body.appendChild(newMask);
    },
    remove : function(){
        document.body.removeChild(document.getElementById("__mask"));
    }
};

