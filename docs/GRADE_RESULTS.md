# Grade Results

The grade results file is produced by ```guac run``` and written to HOME/.scores/RECIPE_NAME/NAME/NAME.grade

The grade results file can be edited by ```guac update```.

## Structure

Grade: Int / Int<br>
Task_Scores: [String:Int]<br>
Assignment: String<br>
Submission_Status: "OnTime" | "Late" | "Missing"<br>
Messages: [String] (Optional)<br>
Task_Results: [Task_Result]<br>

**where Task_Result**

Task_Name: String<br>
Score: Int / Int<br>
Test_Results: [[String: String|List]]

