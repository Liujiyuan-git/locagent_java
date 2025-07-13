package com.example.complex;

import java.util.*;
import java.io.*;

/**
 * 复杂的Java类，包含各种关系
 */
public class ComplexTest extends AbstractBase implements Serializable {
    
    // 字段
    private List<String> items;
    private Map<String, Object> config;
    
    // 内部类
    public class InnerClass {
        private String innerField;
        
        public void innerMethod() {
            System.out.println("Inner method called");
            outerMethod();
        }
    }
    
    // 构造函数
    public ComplexTest() {
        this.items = new ArrayList<>();
        this.config = new HashMap<>();
        initializeData();
    }
    
    // 实例方法
    public void instanceMethod() {
        System.out.println("Instance method called");
        processItems();
        callExternalService();
    }
    
    // 方法调用其他方法
    private void processItems() {
        for (String item : items) {
            processString(item);
        }
        validateData();
    }
    
    private void processString(String str) {
        if (str != null && !str.isEmpty()) {
            str = str.trim();
            items.add(str);
        }
    }
    
    private void validateData() {
        if (items.isEmpty()) {
            throw new IllegalStateException("Items cannot be empty");
        }
    }
    
    private void initializeData() {
        items.add("item1");
        items.add("item2");
        config.put("key1", "value1");
        config.put("key2", 42);
    }
    
    private void callExternalService() {
        try {
            ExternalService service = new ExternalService();
            service.process();
        } catch (Exception e) {
            System.err.println("Error calling external service: " + e.getMessage());
        }
    }
    
    public void outerMethod() {
        System.out.println("Outer method called");
    }
    
    // 重写方法
    @Override
    public void abstractMethod() {
        System.out.println("Abstract method implementation");
    }
    
    @Override
    public String toString() {
        return "ComplexTest{" +
                "items=" + items +
                ", config=" + config +
                '}';
    }
}

// 抽象基类
abstract class AbstractBase {
    protected String baseName;
    
    public AbstractBase() {
        this.baseName = "AbstractBase";
    }
    
    public abstract void abstractMethod();
    
    public void concreteMethod() {
        System.out.println("Concrete method in abstract class");
    }
}

// 接口
interface DataProcessor {
    void processData();
    default void defaultMethod() {
        System.out.println("Default method in interface");
    }
}

// 实现接口的类
class DataProcessorImpl implements DataProcessor {
    @Override
    public void processData() {
        System.out.println("Processing data");
    }
}

// 外部服务类
class ExternalService {
    public void process() {
        System.out.println("External service processing");
    }
}

// 枚举
enum Status {
    PENDING("Pending"),
    PROCESSING("Processing"),
    COMPLETED("Completed"),
    FAILED("Failed");
    
    private final String description;
    
    Status(String description) {
        this.description = description;
    }
    
    public String getDescription() {
        return description;
    }
} 