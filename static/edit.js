$(document).ready(function(){

	$('.edit-slug').css('visibility','hidden');
	$('#post-title').focus();


	$('.btn-url-edit').click(function(){

		if ($('#url-meta').length>0){


			var meta=$('#url-meta').val();

			$('.post-url').text('http://127.0.0.1:8000/'+meta);

			$('.post-url').append("<input type='hidden' name='url' value="+meta+">");

			$('.edit-slug a').text('编辑');

		}
		else{
			var title=$('#post-title').val();

			$('.post-url').text('http://127.0.0.1:8000/').append("<input type='text' id='url-meta'  value="+title+" >");
			$('.edit-slug a').text('确定');

		}

		
	});




})

var ShowIt=function(){


		var title=$('#post-title').val();
		
		if (title!==''){

			$('.edit-slug').css('visibility','visible');

			$('.post-url').text('http://127.0.0.1:8000/'+title);

			$('.post-url').append("<input type='hidden' name='url' value="+title+">");

		}

}




