/*global $, gettext*/
$(function () {
    var $container = $("#passbook-gmaps-result");
    $container.html("<span class='fa fa-cog fa-spin'></span> " + gettext("Loading suggested geolocations…"));
    $.post(
        $container.attr("data-url"),
        {
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        function (data, status) {
            if (data.status === "ok") {
                $container.html("<span class='fa fa-world'></span> " +
                    gettext("Click on one of the following suggestions to fill in the coordinates automatically:"));
                var $ul = $("<ul>");
                for (var i in data.result) {
                    var res = data.result[i];
                    var $li = $("<li>");
                    var $a = $("<a>")
                        .attr("href", "#")
                        .attr("data-lat", res.geometry.location.lat)
                        .attr("data-lng", res.geometry.location.lng)
                        .text(res.formatted_address)
                        .appendTo($li);
                    $ul.append($li);
                }
                $container.append($ul);
                $ul.on("click", "a", function (e) {
                    $("#id_ticketoutput_passbook_longitude").val($(this).attr("data-lng"));
                    $("#id_ticketoutput_passbook_latitude").val($(this).attr("data-lat"));
                    e.preventDefault();
                    return false;
                })
            } else {
                $container.html("<span class='fa fa-exclamation-triangle'></span> " +
                    gettext("Error while loading suggested geolocations."));
            }
        });
});
