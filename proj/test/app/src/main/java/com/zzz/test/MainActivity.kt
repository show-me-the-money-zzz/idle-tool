package com.zzz.test

//import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

//        Intent intent = getPackageManager().getLaunchIntentForPackage("com.ncsoft.lineagew");
//
//        if(null != intent)
//            startActivity(intent); // 앱 실행
//        else
//            Toast.makeText(this, "앱이 설치되어 있지 않습니다.", Toast.LENGTH_SHORT).show();
    }
}