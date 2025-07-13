package com.example;

import java.util.List;
import java.util.ArrayList;

/**
 * Calculator class for basic arithmetic operations
 */
public class Calculator {
    private int result;
    private List<String> history;
    
    public Calculator() {
        this.result = 0;
        this.history = new ArrayList<>();
    }
    
    /**
     * Adds two numbers
     * @param a first number
     * @param b second number
     * @return sum of a and b
     */
    public int add(int a, int b) {
        result = a + b;
        history.add("add(" + a + ", " + b + ") = " + result);
        return result;
    }
    
    /**
     * Subtracts b from a
     * @param a first number
     * @param b second number
     * @return difference of a and b
     */
    public int subtract(int a, int b) {
        result = a - b;
        history.add("subtract(" + a + ", " + b + ") = " + result);
        return result;
    }
    
    /**
     * Multiplies two numbers
     * @param a first number
     * @param b second number
     * @return product of a and b
     */
    public int multiply(int a, int b) {
        result = a * b;
        history.add("multiply(" + a + ", " + b + ") = " + result);
        return result;
    }
    
    /**
     * Divides a by b
     * @param a dividend
     * @param b divisor
     * @return quotient of a and b
     * @throws ArithmeticException if b is zero
     */
    public double divide(int a, int b) {
        if (b == 0) {
            throw new ArithmeticException("Division by zero");
        }
        result = a / b;
        history.add("divide(" + a + ", " + b + ") = " + result);
        return (double) a / b;
    }
    
    /**
     * Gets the current result
     * @return current result
     */
    public int getResult() {
        return result;
    }
    
    /**
     * Gets the calculation history
     * @return list of calculation history
     */
    public List<String> getHistory() {
        return new ArrayList<>(history);
    }
    
    /**
     * Clears the calculator
     */
    public void clear() {
        result = 0;
        history.clear();
    }
}

/**
 * Interface for mathematical operations
 */
interface MathOperation {
    /**
     * Performs a mathematical operation
     * @param a first operand
     * @param b second operand
     * @return result of the operation
     */
    int perform(int a, int b);
}

/**
 * Enum for operation types
 */
enum OperationType {
    ADD("Addition"),
    SUBTRACT("Subtraction"),
    MULTIPLY("Multiplication"),
    DIVIDE("Division");
    
    private final String description;
    
    OperationType(String description) {
        this.description = description;
    }
    
    public String getDescription() {
        return description;
    }
}

/**
 * Advanced calculator that extends basic calculator
 */
public class AdvancedCalculator extends Calculator implements MathOperation {
    private OperationType lastOperation;
    
    public AdvancedCalculator() {
        super();
        this.lastOperation = null;
    }
    
    @Override
    public int perform(int a, int b) {
        switch (lastOperation) {
            case ADD:
                return add(a, b);
            case SUBTRACT:
                return subtract(a, b);
            case MULTIPLY:
                return multiply(a, b);
            case DIVIDE:
                return (int) divide(a, b);
            default:
                return add(a, b);
        }
    }
    
    /**
     * Sets the operation type for the next calculation
     * @param operation the operation type
     */
    public void setOperation(OperationType operation) {
        this.lastOperation = operation;
    }
    
    /**
     * Gets the last operation type
     * @return last operation type
     */
    public OperationType getLastOperation() {
        return lastOperation;
    }
} 