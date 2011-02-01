
$(document).ready(function() {
  jQuery.fn.imdbVisualization = function() {
    this.each(function(){
      s = $(this).find('.stars')
      s.css('display', 'none');
          
      var text = s.text()
      if (text == '' || text == ' ') return;
      
      var t = $('<span class="viz"></span>');
      t.insertBefore(s)
      
      text = text.split(" ", 2);
            
      var votes = parseInt(text[1])
      if(votes < 1000) rvotes = 0
      else if(votes < 6000) rvotes = 1
      else if(votes < 12000) rvotes = 2
      else if(votes < 20000) rvotes = 3
      else if(votes < 33000) rvotes = 4
      else rvotes = 5
            
      var stars = parseFloat(text[0]) / 2
      var full_star_count = Math.floor(stars)
      var partial_star_percent = Math.floor((stars - full_star_count) * 100)
      
      var r = Raphael(t[0], 60, 24)
      
      for(var i = 0; i < full_star_count; i++){
        var p = r.path(path).attr({fill: "#808080", stroke: "#808080", "stroke-width": 1});
        p.scale(0.30, 0.30, 0, 0)
        p.translate(i*12, 0)
      }
            
      var p = r.path(path).attr({fill: "0-#808080-#808080:"+partial_star_percent+"-#fff:"+partial_star_percent+"-#fff", stroke: "#808080", "stroke-width": 0.5});
      p.scale(0.30, 0.30, 0, 0)
      p.translate(full_star_count*12, 0)
            
      for(var i = full_star_count; i < 5; i++){
        var p = r.path(path).attr({fill: "none", stroke: "#808080", "stroke-width": 0.3});
        p.scale(0.30, 0.30, 0, 0)
        p.translate(i*12, 0)
      }
            
      for(var i = 0; i < 5; i++){
        if(i < rvotes) fill = "#808080";
        else fill = "none"
        var p = r.rect(0.5, 15.5, 10, 6, 2).attr({fill: fill, stroke: "#808080", "stroke-width": 0.5});
        p.translate(i*12, 0)
      }
    })
          
    $(this).find('.extrabutton').css('visibility', 'hidden');
    $(this).find('.extrabutton').parent().hover(
      function(){ $(this).children('.extrabutton').css('visibility', ''); },
      function(){ $(this).children('.extrabutton').css('visibility', 'hidden'); }
    )
    return this;
    
  };

  //var s = $('.stars');
  var couch_path = "M0,43v60q0,20,20,20h190q20,0,20-20v-60q0-20-20-20h-5a32,32-50,0,0,-50-15a30,30-50,0,0-40,0a30,30-50,0,0-40,0a32,32-50,0,0-50,15h-5q-20,0-20,20zM35,58h160v5h-160z"
  var path = "M15.999,22.77l-8.884,6.454l3.396-10.44l-8.882-6.454l10.979,0.002l2.918-8.977l0.476-1.458l3.39,10.433h10.982l-8.886,6.454l3.397,10.443L15.999,22.77L15.999,22.77z"
  
  var logo = Raphael($('#logo')[0], 69, 37)
  var couch = logo.path(couch_path).attr({fill: "#f3f3f3", stroke: "none"})
  //logo.text(140, 21, "coucheeb").attr({"class":"logo",fill:"#dfdfdf"})
  couch.scale(0.3, 0.3, 0, 0)
  
  $('#shows_wrapper .movie').imdbVisualization()
        
    
	$("#votes_slider").data("votes", [
    {display: '0', value: 0}, 
		{display: '100', value: 100}, 
    {display: '250', value: 250},
    {display: '500', value: 500},
    {display: '750', value: 750},
    {display: '1k', value: 1000},
    {display: '2k', value: 2000},
    {display: '3k', value: 3000},
    {display: '4k', value: 4000},
    {display: '5k', value: 5000},
    {display: '6k', value: 6000},
    {display: '7k', value: 7000},
    {display: '8k', value: 8000},
    {display: '9k', value: 9000},
    {display: '10k', value: 10000},
    {display: '12k', value: 12000},
    {display: '15k', value: 15000},
    {display: '17k', value: 17000},
    {display: '20k', value: 20000},
    {display: '30k', value: 30000},
    {display: '40k', value: 40000},
    {display: '50k', value: 50000},
    {display: '70k', value: 70000},
    {display: '100k', value: 100000},
    {display: '200k', value: 200000},
    {display: 'No limit', value: '()'}
  ])
  
  $("#votes_slider").data("find_maxmin_votes", function(value){
    if(value == "()") value = 1000000;
    else value = parseInt(value)  
    
    var values = $("#votes_slider").data("votes");
    for(val = 1; val < values.length - 1; val++){
      if(value == values[val - 1]['value']){ return [val - 1, val - 1] }
      if(value == values[val]['value']){ return [val, val] }
      if(value > values[val - 1]['value'] && value < values[val]['value']){ return [val - 1, val]  }
    }
    return [values.length - 1, values.length - 1]
  })
  
  var order = $("#filters input[name=order]").val()
  $("#order li a[rel="+order+"]").parent().addClass("selected");
  var direction = $("#filters input[name=direction]").val()
  $("#direction li a[rel='"+direction+"']").parent().addClass("selected");
  minvotes = $("#filters input[name=minvotes]").val();
  maxvotes = $("#filters input[name=maxvotes]").val();
  minrating = parseFloat($("#filters input[name=minrating]").val());
  maxrating = parseFloat($("#filters input[name=maxrating]").val());
  
  minvotes = $("#votes_slider").data("find_maxmin_votes")(minvotes)[0];  
  maxvotes = $("#votes_slider").data("find_maxmin_votes")(maxvotes)[1];  
    
  $("#votes_slider").slider({
	  range: true,
	  min: 0,
	  max: 25,
	  step: 1,
	  values: [minvotes, maxvotes],
	  slide: function(event, ui) {
	    $(".votes .min").text($('#votes_slider').data('votes')[ui.values[0]].display);
	    $(".votes .max").text($('#votes_slider').data('votes')[ui.values[1]].display);
	    $("#filters input[name='minvotes']").val($('#votes_slider').data('votes')[ui.values[0]].value);
	    $("#filters input[name='maxvotes']").val($('#votes_slider').data('votes')[ui.values[1]].value);
	  }
	});
	
	$(".votes .min").text($('#votes_slider').data('votes')[minvotes].display);
	$(".votes .max").text($('#votes_slider').data('votes')[maxvotes].display);
			
	$("#rating_slider").slider({
	  range: true,
	  min: 0,
	  max: 100,
	  step: 1,
	  values: [minrating*10, maxrating*10],
	  slide: function(event, ui) {
	    $(".rating .min").text(ui.values[0]/10);
	    $(".rating .max").text(ui.values[1]/10);
	    $("#filters input[name='minrating']").val(ui.values[0]/10);
	    $("#filters input[name='maxrating']").val(ui.values[1]/10);
	  }
	});
	
	$(".rating .min").text(minrating);
  $(".rating .max").text(maxrating);
	//});
		 
  //$("#amount").val('$' + $("#slider-range").slider("values", 0) + ' - $' + $("#slider-range").slider("values", 1));
  $('#order li a, #direction li a').attr('href', '#')
  $('#order li a, #direction li a').click(
    function(){ 
      var id = $(this).parent().parent().attr('id');
      $(this).parent().siblings('li').removeClass('selected'); 
      $(this).parent().addClass('selected'); 
      $("#filters input[name='"+id+"']").val($(this).attr('rel'));
      //$('#filters .button').click(function() { $('#filters form').submit(); });
    }
  );
  
  var next = $('#moreitems').attr('href')
  $('#moreitems').attr('href', '#insert');
  $('#moreitems').data('link', next);
  $('#moreitems').click(
    function(){
      //div.insertBefore('a[name=insert]')
      $.get($(this).data('link'), function(data) {
        console.log('Load was performed')
        var $data = $(data)
        var next_link = $data.find('#moreitems').attr('href');
        $('#moreitems').data('link', next_link);
        var ul = $data.find('#shows_wrapper ul')
        ul.find('.movie').imdbVisualization()
        ul.insertBefore('a[name=insert]')
      })
    }
  );
  
  $('.movie').hover(
    function(){
      if($(this).attr('data-cover') == ''){ return }
      var div = $('<div></div>').addClass('tooltip-cover');
      $(this).append(div);	
      var pos = $(this).position();
      var height = parseInt(div.css('height'));
      var left = Math.max(pos.left - 150, 0);
      var top = Math.max(pos.top - height/2 + 20, $(this).parent().position().top);
      div.css('top', top);
      div.css('left', left);
      div.css('background-image', 'url(' + $(this).attr('data-cover') + ')');	
    },
    function(){
      $(this).find(".tooltip-cover").animate({left: -150}, 500, function(){$(this).remove();})
    }
  );
  
  $(window).scroll(function(){
    if ($(window).scrollTop() == $(document).height() - $(window).height()){
      $('#moreitems').click()
    }
  });
})
