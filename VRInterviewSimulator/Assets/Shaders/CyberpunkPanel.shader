Shader "UI/CyberpunkPanel"
{
    Properties
    {
        [PerRendererData]_MainTex("Sprite", 2D) = "white" {}
        _BorderWidth("Border Width", Range(0.01,0.2)) = 0.05
        _LineLength("Line Length", Range(0.05,0.3)) = 0.08
        _LineThickness("Line Thickness", Range(0.001,0.05)) = 0.005
        _DotSize("Dot Size", Range(0.01,0.1)) = 0.02
        _DotHole("Dot Hole", Range(0.005,0.08)) = 0.012
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
            float _LineLength;
            float _LineThickness;
            float _DotSize;
            float _DotHole;

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
                
                // Border
                float2 border = step(uv, _BorderWidth) + step(1.0 - _BorderWidth, uv);
                float isBorder = saturate(border.x + border.y);
                
                // Top-left corner: diagonal + vertical down
                float tlDiag = step(abs((uv.x - _BorderWidth) - (uv.y - (1.0 - _BorderWidth))), _LineThickness) * 
                               step(uv.x, _BorderWidth + _LineLength) * step(1.0 - _BorderWidth - _LineLength, uv.y);
                float tlVert = step(abs(uv.x - (_BorderWidth + _LineLength)), _LineThickness) * 
                               step(uv.y, 1.0 - _BorderWidth - _LineLength) * step(0.5, uv.y);
                float2 tlDotCenter = float2(_BorderWidth + _LineLength, 0.5);
                float tlDotDist = length((uv - tlDotCenter) * float2(2.0, 1.0));
                float tlDot = step(tlDotDist, _DotSize) - step(tlDotDist, _DotHole);
                
                // Bottom-left corner: diagonal + horizontal right
                float blDiag = step(abs((uv.x - _BorderWidth) + (uv.y - _BorderWidth)), _LineThickness) * 
                               step(uv.x, _BorderWidth + _LineLength) * step(uv.y, _BorderWidth + _LineLength);
                float blHoriz = step(abs(uv.y - (_BorderWidth + _LineLength)), _LineThickness) * 
                                step(_BorderWidth + _LineLength, uv.x) * step(uv.x, 0.5);
                float2 blDotCenter = float2(0.5, _BorderWidth + _LineLength);
                float blDotDist = length((uv - blDotCenter) * float2(2.0, 1.0));
                float blDot = step(blDotDist, _DotSize) - step(blDotDist, _DotHole);
                
                // Top-right corner: diagonal + horizontal left (no dot)
                float trDiag = step(abs((uv.x - (1.0 - _BorderWidth)) + (uv.y - (1.0 - _BorderWidth))), _LineThickness) * 
                               step(1.0 - _BorderWidth - _LineLength, uv.x) * step(1.0 - _BorderWidth - _LineLength, uv.y);
                float trHoriz = step(abs(uv.y - (1.0 - _BorderWidth - _LineLength)), _LineThickness) * 
                                step(0.5, uv.x) * step(uv.x, 1.0 - _BorderWidth - _LineLength);
                
                // Bottom-right corner: diagonal + vertical up
                float brDiag = step(abs((uv.x - (1.0 - _BorderWidth)) - (uv.y - _BorderWidth)), _LineThickness) * 
                               step(1.0 - _BorderWidth - _LineLength, uv.x) * step(uv.y, _BorderWidth + _LineLength);
                float brVert = step(abs(uv.x - (1.0 - _BorderWidth - _LineLength)), _LineThickness) * 
                               step(0.5, uv.y) * step(uv.y, 1.0 - _BorderWidth - _LineLength);
                float2 brDotCenter = float2(1.0 - _BorderWidth - _LineLength, 0.5);
                float brDotDist = length((uv - brDotCenter) * float2(2.0, 1.0));
                float brDot = step(brDotDist, _DotSize) - step(brDotDist, _DotHole);
                
                // Combine all elements
                float lines = tlDiag + tlVert + blDiag + blHoriz + trDiag + trHoriz + brDiag + brVert;
                float dots = tlDot + blDot + brDot;
                
                // Light gray background, black lines/border/dots
                float elements = saturate(isBorder + lines + dots);
                float3 color = lerp(float3(0.7, 0.7, 0.7), float3(0, 0, 0), elements);
                
                return fixed4(color, 0.9);
            }
            ENDCG
        }
    }
}