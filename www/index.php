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
   $galleryDir = 'thumbnails/';
 $filelist = glob("$galleryDir{*.jpg,*.gif,*.png,*.jpeg}", GLOB_BRACE);
 rsort($filelist);
   foreach($filelist as $photo) {
     $imgName = explode("/", $photo);
     $imgName = end($imgName);
?>
<a href="/montages/<?php echo $imgName;?>">
<img src='<?php echo $photo;?>' class='img-thumbnail'>
</a>
<?php
   //    echo '<a href="/montages/'+$imgName+'">';
 //    echo "<a href='$imgName'>";
  //   echo "'$imgName'";
 //    echo "<img src='$photo' class='img-thumbnail'>";
 //    echo "</a>";
   }
   ?>
		</div>
	</div>
</div>





  </body>
</html>




<!DOCTYPE html>
<html>
 <head>
   <title>PHP Gallery</title>
 </head>
 <body>
   
 </body>
</html>