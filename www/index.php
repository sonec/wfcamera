<!DOCTYPE html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="css/bootstrap.min.css" >
  </head>
  <body>


    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="js/jquery-3.2.1.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
<nav class="navbar navbar-light bg-light">
  <span class="h3" class="navbar-brand mb-0">Photo Booth</span>
</nav>
<div class="container-fluid">
	<div class="row">
    		<div class="col">


<?php
/*
   $galleryDir = 'thumbnails/';
 $filelist = glob("$galleryDir{*.jpg,*.gif,*.png,*.jpeg}", GLOB_BRACE);
 rsort($filelist);
   foreach($filelist as $photo) {
     $imgName = explode("/", $photo);
     $imgName = end($imgName);
?>
<a href="/montages/<?php echo $imgName; ?>">
<img src='<?php echo $photo; ?>' class='img-thumbnail'>
</a>

			
<?php
*/
			
$folder = 'thumbnails/';
$filetype = '*.*';    
$files = glob($folder.$filetype);    
$total = count($files);    
$per_page = 6;    
$last_page = (int)($total / $per_page);    
if(isset($_GET["page"])  && ($_GET["page"] <=$last_page) && ($_GET["page"] > 0) ){
    $page = $_GET["page"];
    $offset = ($per_page + 1)*($page - 1);      
}else{
    echo "Page out of range showing results for page one";
    $page=1;
    $offset=0;      
}    
$max = $offset + $per_page;    
if($max>$total){
    $max = $total;
}
	       //print_r($files);
    echo "Processsing page : $page offset: $offset max: $max total: $total last_page: $last_page";        
    show_pagination($page, $last_page);        
    for($i = $offset; $i< $max; $i++){
        $file = $files[$i];
        $path_parts = pathinfo($file);
        $filename = $path_parts['filename'];        
        echo '       
                <a href="'.$file.'"><img class="img-thumbnail" src="'.$file.'" alt="'.$filename.'"></a>
        ';                
    }        
    show_pagination($page, $last_page);

function show_pagination($current_page, $last_page){
    echo '<nav aria-label="Page navigation example">
  <ul class="pagination">
    ';
    if( $current_page > 1 ){
        echo ' <li class="page-item"><a class="page-link" href="?page='.($current_page-1).'">Previous </a></li> ';
    }
    if( $current_page < $last_page ){
        echo ' <li class="page-item"><a class="page-link"  href="?page='.($current_page+1).'"> Next&gt;&gt; </a></li> ';  
    }
    echo '</ul>
</nav>';
	
}

?>
		</div>
	</div>
</div>





  </body>
</html>
