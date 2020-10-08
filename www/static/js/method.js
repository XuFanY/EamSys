/*根据id获取对象*/
function $(str) {
    return document.getElementById(str);
}
 
var loc = $('location');
var prov = $('prov');
var city = $('city');
var country = $('country');

/*用于保存当前所选的省市区*/
var current = {
    prov: '',
    city: '',
    country: ''
};

/*自动加载省份列表*/
(function showProv() {
    var len = province.length;
    for (var i = 0; i < len; i++) {
        var provOpt = document.createElement('option');
        provOpt.innerText = province[i]['name'];
        provOpt.value = i;
        prov.appendChild(provOpt);
    }
})();

/*根据所选的省份来显示城市列表*/
function showCity(obj) {
    var val = obj.options[obj.selectedIndex].value;
    if (val != current.prov) {
        current.prov = val;
        loc.value = '';
    }
    //console.log(val);
    if (val != null) {
        city.length = 1;
        var cityLen = province[val]["city"].length;
        for (var j = 0; j < cityLen; j++) {
            var cityOpt = document.createElement('option');
            cityOpt.innerText = province[val]["city"][j].name;
            cityOpt.value = j;
            city.appendChild(cityOpt);
        }
    }
}

/*根据所选的城市来显示县区列表*/
function showCountry(obj) {
    var val = obj.options[obj.selectedIndex].value;
    current.city = val;
    if (val != null) {
        country.length = 1; //清空之前的内容只留第一个默认选项
        var countryLen = province[current.prov]["city"][val].districtAndCounty.length;
        if (countryLen == 0) {
            loc.value = province[current.prov].name + '-' + province[current.prov]["city"][current.city].name;
            return;
        }
        for (var n = 0; n < countryLen; n++) {
            var countryOpt = document.createElement('option');
            countryOpt.innerText = province[current.prov]["city"][val].districtAndCounty[n];
            countryOpt.value = n;
            country.appendChild(countryOpt);
        }
    }
}

/*选择县区之后的处理函数*/
function selecCountry(obj) {
    current.country = obj.options[obj.selectedIndex].value;
    if ((current.city != null) && (current.country != null)) {
        loc.value = province[current.prov].name + '-' + province[current.prov]["city"][current.city].name + '-' + province[current.prov]["city"][current.city].districtAndCounty[current.country];
    }
}

