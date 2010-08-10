<?php

$user = $_GET['user'];
$pass = $_GET['pass'];
$data = stripslashes($_GET['data']);


#$user = $_POST['user'];
#$pass = $_POST['pass'];
#$data = $_POST['data'];


if ($user == 'vasco' && $pass = 'password')
{
    $con = mysql_connect("localhost","root","admin");
    if (!$con)
    {
        die('Could not connect: ' . mysql_error());
    }
    
    mysql_select_db("movie", $con);

    //echo $data;
    $json = json_decode($data);
    foreach($json->show as $show){
        $imgfile = $show->imgfile;
        $link = $show->link;
        $desc = $show->desc;
        $name = $show->name;
        $query = "INSERT INTO Tvshow (name, imgfile, link, description) VALUES ('$name', '$imgfile', '$link', '$desc')";
        echo $query;
        $res = mysql_query($query, $con);
        if (!$res)
        {
            die('Error: ' . mysql_error());
        }
    }
    
    foreach($json->releases as $rls){
        echo $rls->name . "\n";
        if($rls->is_featured){
            echo $rls->show;
        }
    }
    
    mysql_close($con);
}
else{
    echo "404";
}


?>
