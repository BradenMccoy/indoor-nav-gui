import cv2
import camera_input
import os

WINDOW = "Indoor Nav"

def test(test_name):
    print("Testing for "+test_name+"---------------")
    if test_name == "empty":
        print("--THERE SHOULD BE NO WARNINGS OR DANGER HERE--")
    path, dirs, files = next(os.walk("testing/test_"+test_name))
    file_count = len(files)

    reference = camera_input.get_reference()

    danger_count = 0
    warning_count = 0
    safe_count = 0

    # Test test_name
    for index in range(0,file_count): 
        dummy_frame = cv2.imread("testing/test_"+test_name+"/image"+str(index)+".png", cv2.IMREAD_UNCHANGED) 

        danger, result = camera_input.analyze_frame(dummy_frame, reference)

        if danger >= 7:
            danger_count = danger_count + 1
        elif danger >= 3:
            warning_count = warning_count + 1
        else:
            safe_count = safe_count + 1

    print("Safe frames:      "+str(safe_count))
    print("Warning frames:   "+str(warning_count))
    print("Dangerous frames: "+str(danger_count))

    print("Finished testing for "+test_name+"---------------\n")

if __name__ == '__main__':
    test("basket")
    test("drop")
    test("empty")
    test("mug")
    test("table")
    test("wall")

