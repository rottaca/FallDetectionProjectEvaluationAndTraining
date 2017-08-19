#include "opencv2/objdetect/objdetect.hpp"
 #include "opencv2/highgui/highgui.hpp"
 #include "opencv2/imgproc/imgproc.hpp"

 #include <iostream>
 #include <stdio.h>

 using namespace std;
 using namespace cv;

 /** Function Headers */
 void detectAndDisplay( Mat frame );

 /** Global variables */
 String face_cascade_name = "cascade.xml";
 CascadeClassifier cascade;
 string window_name = "Capture - Face detection";
 RNG rng(12345);

 /** @function main */
 int main( int argc, const char** argv )
 {
   if(argc < 3){
     cout << "Invalid arguments!" << endl;
    return -1;
   }

   //-- 1. Load the cascades
   if( !cascade.load( argv[1] ) ){ printf("--(!)Error loading classifier: %s\n", argv[1]); return -1; };
   for(int i = 2; i < argc-2;i++){
     Mat frame = imread(argv[i], CV_LOAD_IMAGE_COLOR);
     if( !frame.empty() )
     {
        detectAndDisplay( frame );
     }
     else{
        cout << "Invalid image: " << argv[i] << endl;
        return -1;
     }
 
     int c = waitKey();
   }
   return 0;
 }

/** @function detectAndDisplay */
void detectAndDisplay( Mat frame )
{
  std::vector<Rect> objects;
  Mat frame_gray;

  cvtColor( frame, frame_gray, CV_BGR2GRAY );
  equalizeHist( frame_gray, frame_gray );

  //-- Detect objects
  cascade.detectMultiScale( frame_gray, objects, 1.1, 2, 0|CV_HAAR_SCALE_IMAGE, Size(10, 10) );

  for( size_t i = 0; i < objects.size(); i++ )
  {
    rectangle(frame, objects[i], Scalar(255, 0, 0));
  }
  //-- Show what you got
  imshow( window_name, frame );
 }
