import json
import os
import sys
from typing import List, Dict, Union

class CloudResourceOptimizer:
    def __init__(self, data: List[Dict[str, Union[str, int, float]]]):
        self.data = data
        self.validation_report = {}

    def validate_data(self) -> bool:
        """
        Validate input data according to specified criteria
        """
        self.validation_report = {
            'total_applications': len(self.data),
            'fields_check': {},
            'is_valid': True
        }

        for idx, record in enumerate(self.data, 1):
            # Check for required fields
            required_fields = [
                'application_id', 'current_resources', 'user_demand', 
                'max_capacity', 'performance_threshold', 'scaling_factor'
            ]
            
            missing_fields = [
                field for field in required_fields 
                if field not in record or record[field] is None
            ]
            
            if missing_fields:
                print(f"ERROR: Missing required field(s): {missing_fields} in row {idx}")
                self.validation_report['is_valid'] = False
                return False

            # Validate field types and ranges
            try:
                record['current_resources'] = int(record['current_resources'])
                record['user_demand'] = int(record['user_demand'])
                record['max_capacity'] = int(record['max_capacity'])
                record['performance_threshold'] = float(record['performance_threshold'])
                record['scaling_factor'] = float(record['scaling_factor'])
            except ValueError:
                print(f"ERROR: Invalid numeric values in row {idx}")
                self.validation_report['is_valid'] = False
                return False

            # Additional range validations
            if (record['current_resources'] <= 0 or 
                record['user_demand'] <= 0 or 
                record['max_capacity'] <= 0 or 
                record['scaling_factor'] <= 0 or 
                not (0 <= record['performance_threshold'] <= 100)):
                print(f"ERROR: Values out of acceptable range in row {idx}")
                self.validation_report['is_valid'] = False
                return False

        return True

    def calculate_metrics(self, record: Dict[str, Union[str, int, float]]) -> Dict[str, Union[float, str]]:
        """
        Calculate detailed metrics for a single application record
        """
        # Predicted Demand Calculation
        # $$ \text{Predicted Demand} = \text{user_demand} \times \text{scaling_factor} $$
        predicted_demand = round(
            record['user_demand'] * record['scaling_factor'], 
            2
        )

        # Resource Utilization Ratio Calculation
        # $$ \text{Resource Utilization Ratio} = \frac{\text{Predicted Demand}}{\text{current_resources}} \times 100 $$
        resource_utilization_ratio = round(
            (predicted_demand / record['current_resources']) * 100, 
            2
        )

        # Capacity Margin Calculation
        # $$ \text{Capacity Margin} = \frac{(\text{max_capacity} - \text{current_resources})}{\text{max_capacity}} \times 100 $$
        capacity_margin = round(
            ((record['max_capacity'] - record['current_resources']) / record['max_capacity']) * 100, 
            2
        )

        # Composite Resource Score Calculation
        # $$ \text{Composite Score} = (\text{Capacity Margin} \times 0.4) + ((100 - \text{Resource Utilization Ratio}) \times 0.6) $$
        composite_score = round(
            (capacity_margin * 0.4) + ((100 - resource_utilization_ratio) * 0.6), 
            2
        )

        # Efficiency Ratio Calculation
        # $$ \text{Efficiency Ratio} = \frac{\text{current_resources}}{\text{Predicted Demand}} $$
        efficiency_ratio = round(
            record['current_resources'] / predicted_demand, 
            2
        )

        # Determine Recommendation
        if (composite_score >= 70 and 
            0.95 <= efficiency_ratio <= 1.05 and 
            resource_utilization_ratio <= record['performance_threshold']):
            recommendation = "Optimal - Maintain current allocation"
        else:
            recommendation = "Needs Adjustment - Consider scaling resources"

        return {
            'predicted_demand': predicted_demand,
            'resource_utilization_ratio': resource_utilization_ratio,
            'capacity_margin': capacity_margin,
            'composite_score': composite_score,
            'efficiency_ratio': efficiency_ratio,
            'recommendation': recommendation
        }

    def generate_report(self) -> str:
        """
        Generate comprehensive markdown report
        """
        if not self.validate_data():
            return "Data validation failed. Please review and resubmit."

        report = "# Cloud Resource Allocation Summary\n"
        report += f"- Total Applications Evaluated: {len(self.data)}\n\n"

        for idx, record in enumerate(self.data, 1):
            metrics = self.calculate_metrics(record)
            
            report += f"## Application {record['application_id']}\n\n"
            report += "### Input Data:\n"
            report += f" - Current Resources: {record['current_resources']}\n"
            report += f" - User Demand: {record['user_demand']}\n"
            report += f" - Maximum Capacity: {record['max_capacity']}\n"
            report += f" - Performance Threshold (%): {record['performance_threshold']}\n"
            report += f" - Scaling Factor: {record['scaling_factor']}\n\n"

            report += "### Detailed Calculations:\n\n"
            report += "1. Predicted Demand Calculation:\n"
            report += "   - Formula: $$ \\text{Predicted Demand} = \\text{user_demand} \\times \\text{scaling_factor} $$\n"
            report += f"   - Final Predicted Demand: {metrics['predicted_demand']}\n\n"

            report += "2. Resource Utilization Ratio Calculation:\n"
            report += "   - Formula: $$ \\text{Resource Utilization Ratio} = \\frac{\\text{Predicted Demand}}{\\text{current_resources}} \\times 100 $$\n"
            report += f"   - Final Resource Utilization Ratio: {metrics['resource_utilization_ratio']}%\n\n"

            report += "3. Capacity Margin Calculation:\n"
            report += "   - Formula: $$ \\text{Capacity Margin} = \\frac{(\\text{max_capacity} - \\text{current_resources})}{\\text{max_capacity}} \\times 100 $$\n"
            report += f"   - Final Capacity Margin: {metrics['capacity_margin']}%\n\n"

            report += "4. Composite Resource Score Calculation:\n"
            report += "   - Formula: $$ \\text{Composite Score} = (\\text{Capacity Margin} \\times 0.4) + ((100 - \\text{Resource Utilization Ratio}) \\times 0.6) $$\n"
            report += f"   - Final Composite Score: {metrics['composite_score']}\n\n"

            report += "5. Efficiency Ratio Calculation:\n"
            report += "   - Formula: $$ \\text{Efficiency Ratio} = \\frac{\\text{current_resources}}{\\text{Predicted Demand}} $$\n"
            report += f"   - Final Efficiency Ratio: {metrics['efficiency_ratio']}\n\n"

            report += "### Final Recommendation:\n"
            report += f" - Composite Score: {metrics['composite_score']}\n"
            report += f" - Resource Utilization Ratio: {metrics['resource_utilization_ratio']}%\n"
            report += f" - Efficiency Ratio: {metrics['efficiency_ratio']}\n"
            report += f" - Status: {metrics['recommendation']}\n\n"

        return report

def generate_sample_data() -> List[Dict[str, Union[str, int, float]]]:
    """
    Generate sample cloud resource data for demonstration
    """
    return [
    {
      "application_id": "AppAlpha",
      "current_resources": 50,
      "user_demand": 45,
      "max_capacity": 100,
      "performance_threshold": 75,
      "scaling_factor": 1.2
    },
    {
      "application_id": "AppBeta",
      "current_resources": 70,
      "user_demand": 60,
      "max_capacity": 140,
      "performance_threshold": 80,
      "scaling_factor": 1.15
    },
    {
      "application_id": "AppGamma",
      "current_resources": 80,
      "user_demand": 70,
      "max_capacity": 150,
      "performance_threshold": 85,
      "scaling_factor": 1.1
    },
    {
      "application_id": "AppDelta",
      "current_resources": 90,
      "user_demand": 75,
      "max_capacity": 160,
      "performance_threshold": 80,
      "scaling_factor": 1.0
    },
    {
      "application_id": "AppEpsilon",
      "current_resources": 65,
      "user_demand": 55,
      "max_capacity": 120,
      "performance_threshold": 70,
      "scaling_factor": 1.3
    },
    {
      "application_id": "AppZeta",
      "current_resources": 100,
      "user_demand": 95,
      "max_capacity": 180,
      "performance_threshold": 90,
      "scaling_factor": 1.05
    },
    {
      "application_id": "AppEta",
      "current_resources": 85,
      "user_demand": 80,
      "max_capacity": 170,
      "performance_threshold": 75,
      "scaling_factor": 1.15
    },
    {
      "application_id": "AppTheta",
      "current_resources": 75,
      "user_demand": 65,
      "max_capacity": 130,
      "performance_threshold": 85,
      "scaling_factor": 1.2
    },
    {
      "application_id": "AppIota",
      "current_resources": 60,
      "user_demand": 50,
      "max_capacity": 110,
      "performance_threshold": 80,
      "scaling_factor": 0.95
    },
    {
      "application_id": "AppKappa",
      "current_resources": 95,
      "user_demand": 90,
      "max_capacity": 200,
      "performance_threshold": 90,
      "scaling_factor": 1.1
    }
  ]

def load_json_data(file_path: str = None) -> List[Dict[str, Union[str, int, float]]]:
    """
    Load cloud resource data from a JSON file or use default data
    """
    # If no file path is provided, return sample data
    if not file_path:
        return generate_sample_data()

    # If a file path is provided, try to load it
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return generate_sample_data()
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file {file_path}")
        return generate_sample_data()

def main():
    """
    Main function to demonstrate cloud resource optimization
    """
    # Option 1: Use default sample data
    print("Cloud Resource Optimization Report:")
    data = load_json_data()  # No argument uses sample data
    
    # Create optimizer and generate report
    optimizer = CloudResourceOptimizer(data)
    report = optimizer.generate_report()
    
    # Print the report
    print(report)

    # Option 2: Uncomment and modify to load from a specific JSON file
    # json_file_path = 'path/to/your/cloud_resources.json'
    # data = load_json_data(json_file_path)
    # optimizer = CloudResourceOptimizer(data)
    # report = optimizer.generate_report()
    # print(report)

if __name__ == "__main__":
    main()