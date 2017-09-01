#include "opencv2/objdetect/objdetect.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

#include <iostream>
#include <fstream>
#include <stdio.h>
#include <string>
#include <sstream>
#include <vector>
#include <iterator>

using namespace std;
using namespace cv;

template<typename Out>
void split(const std::string &s, char delim, Out result) {
    std::stringstream ss;
    ss.str(s);
    std::string item;
    while (std::getline(ss, item, delim)) {
        *(result++) = item;
    }
}

std::vector<std::string> split(const std::string &s, char delim) {
    std::vector<std::string> elems;
    split(s, delim, std::back_inserter(elems));
    return elems;
}
/** Function Headers */
bool detectAndDisplay( Mat frame, Rect label, bool show );

/** Global variables */
String face_cascade_name = "cascade.xml";
CascadeClassifier cascade;
string window_name = "Capture - Face detection";
RNG rng(12345);

struct Label{
  Rect rect;
  string fileName;
};
vector<struct Label> fallLabels;

/** @function main */
int main( int argc, const char** argv )
{
 if(argc != 3 && argc != 4){
   cout << "Invalid arguments!" << endl;
  return -1;
 }

 //-- 1. Load the cascades
 if( !cascade.load( argv[1] ) ){ printf("--(!)Error loading classifier: %s\n", argv[1]); return -1; };
 std::string baseFolder = argv[2];
 std::string labelFile = baseFolder + "/info.dat";
 std::string negFile = baseFolder + "/bg.txt";
 std::ifstream file;
 file.open(labelFile.c_str());
 std::string line;
 while (std::getline(file, line)) {
   std::vector<std::string> list = split(line, ' ');
  struct Label l;
  l.rect = Rect(atoi(list[2].c_str()),
                atoi(list[3].c_str()),
                atoi(list[4].c_str()),
                atoi(list[5].c_str()));
  l.fileName = list[0];

   fallLabels.push_back(l);
 }
 file.close();
 
 std::vector<cv::String> negFilenames;
 file.open(negFile.c_str());
 while (std::getline(file, line)) {
   negFilenames.push_back(baseFolder + "/" + line);
 }

 size_t TP = 0,TN = 0,FP = 0,FN = 0;

  for(int i = 0; i < fallLabels.size();i++){
    if(i % 50 == 0){
      cout << "\rFrame: " << i+1 << " (" << (float)100*(i+1)/(fallLabels.size()+negFilenames.size()) << "%)";
      cout.flush();
     }
    Mat frame = imread(baseFolder + "/" + fallLabels[i].fileName, CV_LOAD_IMAGE_COLOR);
    if( !frame.empty() )
    {
       if(detectAndDisplay( frame, fallLabels[i].rect ,argc==4 ))
         TP++;
       else
         FN++;
    }
    else{
       cout << "Invalid image: " << argv[i] << endl;
       return -1;
    }
  }

 for(int i = 0; i < negFilenames.size();i++){
   if((i+fallLabels.size()-1) % 50 == 0){
    cout << "\rFrame: " << i+1+fallLabels.size() << " (" << (float)100*(i+1+fallLabels.size())/(fallLabels.size()+negFilenames.size()) << "%)";
    cout.flush();
   }

   Mat frame = imread(negFilenames[i], CV_LOAD_IMAGE_COLOR);
   if( !frame.empty() )
   {
      if(detectAndDisplay( frame, Rect() ,argc==4))
        FP++;
      else
        TN++;
   }
   else{
      cout << "Invalid image: " << argv[i] << endl;
      return -1;
   }
 }

 cout << "\nSummary" << endl;
 cout << "TPR: " << (double)TP/(TP+FN) << endl;
 cout << "TNR: " << (double)TN/(TN+FP) << endl;
 cout << "FPR: " << (double)FP/(FP+TN) << endl;
 cout << "FNR: " << (double)FN/(FN+TP) << endl;
 cout << "P: " << FN+TP << endl;
 cout << "N: " << FP+TN << endl;
 return 0;
}

/** @function detectAndDisplay */
bool detectAndDisplay( Mat frame, Rect label, bool show )
{
  std::vector<Rect> objects;
  Mat frame_gray;

  cvtColor( frame, frame_gray, CV_BGR2GRAY );
  equalizeHist( frame_gray, frame_gray );

  //-- Detect objects
  cascade.detectMultiScale( frame_gray, objects, 1.1, 2, 0|CV_HAAR_SCALE_IMAGE, Size(10, 10) );
  bool valid = objects.size() > 0;
  if(show)
    rectangle(frame, label, Scalar(0, 0, 255));
  for( size_t i = 0; i < objects.size(); i++ )
  {
    if((objects[i] & label).area() > 100)
      valid |= true;
    if(show)
      rectangle(frame, objects[i], Scalar(255, 0, 0));
  }
  //-- Show what you got
  if(show){
    imshow( window_name, frame );
    waitKey();
  }
  return valid;
 }
