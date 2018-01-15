<?php 

$docroot = '/home/pi/wfcamera/www/';
if (isset($_POST['print']))
{
exec('lp -d CANON_SELPHY_CP1200 '.$docroot.$_POST['path']);
$message = "Printing";
//exec('ls');
//exec('lp -d CANON_SELPHY_CP910'.$_POST['path']);
} else if (isset($_POST['printN']))
{
exec('lp -d CANON_SELPHY_CP1200N -raw '.$docroot.$_POST['path']);
$message = "Printing";
}
?>

<!DOCTYPE html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="static/css/bootstrap.min.css" >
  </head>
  <body>


    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="static/js/jquery-3.2.1.min.js"></script>
    <script src="static/js/popper.js"></script>
    <script src="static/js/bootstrap.min.js"></script>
<nav class="navbar navbar-light bg-light">
  <span class="h3" class="navbar-brand mb-0">Printerface</span>
</nav>
<div class="container">
<?php
	if (isset($message)) {
	echo '<div class="alert alert-success alert-dismissible fade show" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>Sent to Printer</div>';
	}
?>
	<div class="row mt-2 justify-content-center">
    	<!--	<div class="col"> -->

<!-- Modal -->
<div class="modal fade" id="exampleModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg bd-example-modal-lg" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">Modal title</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <img class="img-fluid" src="">
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
        <form method="POST"><input id="hid" type="hidden" name="path" value="" />
<input type="submit" name="print" value="Print" class="btn btn-primary" />
<input id="hid" type="hidden" name="path" value="" />
<input type="submit" name="printN" value="Print Wireless" class="btn btn-primary ml-1" />
</form>
      </div>
    </div>
  </div>
</div>
<?php
			
$folder = 'thumbnails/';
$filetype = '*.*';    
$files = glob($folder.$filetype);    
rsort($files);
$total = count($files);    
$per_page = 6;    
$last_page = (int)($total / $per_page);    
if(isset($_GET["page"])  && ($_GET["page"] <=$last_page) && ($_GET["page"] > 0) ){
    $page = $_GET["page"];
    $offset = ($per_page + 1)*($page - 1);      
}else{
    $page=1;
    $offset=0;      
}    
$max = $offset + $per_page;    
if($max>$total){
    $max = $total;
}


    for($i = $offset; $i< $max; $i++){
        $file = $files[$i];
        $path_parts = pathinfo($file);
        $filename = $path_parts['filename'];        

        echo '<div class="card"><a class="card-link" data-filename="'.$filename.'" data-path="prints/'.$filename.'.jpg" data-toggle="modal" data-target="#exampleModal"><img class="card-img-top" src="'.$file.'"><div class="card-body"><p class="card-text text-center">'.$filename.'</p></div></a></div>';
    }        

function show_pagination($current_page, $last_page){
    echo '<nav aria-label="Page navigation example text-center">
  <ul class="pagination pagination-lg justify-content-center">
    ';
    if( $current_page > 1 ){
        echo ' <li class="page-item"><a class="page-link" href="?page='.($current_page-1).'">Next </a></li> ';
    }
    if( $current_page < $last_page ){
        echo ' <li class="page-item"><a class="page-link"  href="?page='.($current_page+1).'">Previous </a></li> ';  
    }
    echo '</ul>
</nav>';
	
}
?>
		


		<!--</div>-->
	</div>
	<div class="row mt-2">
		<div class="col">
			<?php show_pagination($page, $last_page); ?>
		</div>
	</div>

</div>

<script>

$('#exampleModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget) // Button that triggered the modal
  var imgtitle = button.data('filename') // Extract info from data-* attributes
  var imgsrc = button.data('path') // Extract info from data-* attributes
  // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  var modal = $(this)
  modal.find('.modal-title').text(imgtitle)
  modal.find('.modal-body img').attr('src',imgsrc)
  modal.find('.modal-footer input#hid').val(imgsrc)
})
</script>



  </body>
</html>

