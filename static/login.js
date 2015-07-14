$(document).ready(function(){


	$("body").keydown(function(){

		if(event.keyCode==13) { 
   			$(".btn-default.btn-blue").click(); 
 	 	} 
	});



	$('.btn-default.btn-blue').click(function(){
		
		var username=$('#username').val();
		var passwd=$('#passwd').val();

		$.post("/login",
	    	{
	      	username:username,
	      	passwd:passwd
	    	},
	    	function(data,status){
	      	
	      	if (data=='yes'){

	      		$(window.location).attr('href', '/blog');
	      	}
	      	else{

	      		for(var i=1;i<8;i++){
  					if (i%2==0){

  						$('.login-info').animate({left:'10px'},50);
  					}
  					else{

  						$('.login-info').animate({left:'-10px'},50);
  					}

  				}
  				$('.login-info').animate({left:0},10);
  				$('#username').val('');
  				$('#passwd').val('');
	      	}
	      	
	    	}
	    	);
		});
});
