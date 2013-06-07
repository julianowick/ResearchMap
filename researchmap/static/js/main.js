var map;
function initialize() {
    var mapOptions = {
        zoom: 2,
        center: new google.maps.LatLng(0, 0),
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
}
google.maps.event.addDomListener(window, 'load', initialize);

var geocoder = new google.maps.Geocoder();
function markAuthor(author){
    geocoder.geocode({ address: author.Affiliation}, function(results, status){
        console.log(results);
        console.log(status);
        console.log(author);
        if (results == null) return;
        else if(results.length > 0){
            //Use only one result per author
            val = results[0];
            //author = authors[cur_author-1]
            var contentString = 
                '<div class="author-info">'+
                '<div class="author-photo"><img src="' + author.Photo + '"/></div>'+
                '<div class="author-details">'+
                '<h2>' + author.Name + '</h2>'+
                '<p>' + author.Affiliation + '</p>';
            if (author.Homepage != null){
                contentString += '<p><a href="'+ author.Homepage +'" target="_blank">Homepage</a></p>';
            }
            contentString += 
                '<p><a href="'+ author.URL +'" target="_blank">Google Scholar</a></p>'+
                '</div></div>';
            var infowindow = new google.maps.InfoWindow({
                content: contentString
            });
            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(val['geometry']['location']['jb'], val['geometry']['location']['kb']),
                map: map,
                title: val['formatted_address'],
            //icon: val['icon']
            //    alert(val);
            });
            google.maps.event.addListener(marker, 'click', function() {
                infowindow.open(map, marker);
            });
        }
    });
}
function searchMarker(){
    $.getJSON('scholar/' + $('#queryField').val(), function(data) {
        $.each(data, function(key, val) {
            //alert(val['Affiliation']);
            markAuthor(val);
        });
    });
    return false;
}

