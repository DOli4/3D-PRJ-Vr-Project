Shader "UI/CyberpunkButton"
{
    Properties
    {
        [PerRendererData]_MainTex("Sprite", 2D) = "white" {}
        _BorderWidth("Border Width", Range(0.01,0.2)) = 0.12
    }

    SubShader
    {
        Tags
        {
            "Queue"="Transparent"
            "RenderType"="Transparent"
        }

        Blend One Zero
        ZWrite Off
        Cull Off
        ColorMask RGB

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            float _BorderWidth;

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
            };

            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                float2 uv = i.uv;
                
                // Border detection
                float2 border = step(uv, _BorderWidth) + step(1.0 - _BorderWidth, uv);
                float isBorder = saturate(border.x + border.y);
                
                float lineThickness = 0.0018;
                float dotSize = 0.027;
                float dotHole = 0.0144;
                
                // Left line 85% from middle (0.325) going halfway down - extend to border
                float leftLine = step(abs(uv.x - 0.325), lineThickness) * step(uv.y, 0.5) * step(_BorderWidth, uv.y);
                float2 leftCenter = float2(0.325, 0.5);
                float leftDist = length((uv - leftCenter) * float2(2.0, 1.0));
                float leftDotOuter = step(leftDist, dotSize);
                float leftDotInner = step(leftDist, dotHole);
                float leftDot = leftDotOuter - leftDotInner;
                
                // Right line 85% from middle (0.675) going halfway up - extend to border
                float rightLine = step(abs(uv.x - 0.675), lineThickness) * step(0.5, uv.y) * step(uv.y, 1.0 - _BorderWidth);
                float2 rightCenter = float2(0.675, 0.5);
                float rightDist = length((uv - rightCenter) * float2(2.0, 1.0));
                float rightDotOuter = step(rightDist, dotSize);
                float rightDotInner = step(rightDist, dotHole);
                float rightDot = rightDotOuter - rightDotInner;
                
                float lines = leftLine + rightLine;
                float dots = leftDot + rightDot;
                
                // Black border, lines and dots, white fill
                float color = 1.0 - saturate(isBorder + lines + dots);
                
                return fixed4(color, color, color, 0.9);
            }
            ENDCG
        }
    }
}