// Test script for toaster functionality
// This can be used to test the toaster system

document.addEventListener('DOMContentLoaded', () => {
    // Add test buttons to pages (for development/testing only)
    if (window.location.search.includes('test=toaster')) {
        const testDiv = document.createElement('div');
        testDiv.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            direction: rtl;
        `;
        
        testDiv.innerHTML = `
            <h6 style="margin: 0 0 10px 0; font-weight: bold;">تست توستر</h6>
            <button onclick="showSuccessToast('این یک پیام موفقیت‌آمیز تست است!')" style="margin: 2px; padding: 5px 10px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer;">موفقیت</button>
            <button onclick="showErrorToast('این یک پیام خطای تست است!')" style="margin: 2px; padding: 5px 10px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer;">خطا</button>
            <button onclick="showWarningToast('این یک پیام هشدار تست است!')" style="margin: 2px; padding: 5px 10px; background: #f59e0b; color: white; border: none; border-radius: 4px; cursor: pointer;">هشدار</button>
            <button onclick="showInfoToast('این یک پیام اطلاعاتی تست است!')" style="margin: 2px; padding: 5px 10px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;">اطلاعات</button>
        `;
        
        document.body.appendChild(testDiv);
    }
});
