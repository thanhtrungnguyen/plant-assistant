import Image, { ImageProps } from "next/image";
import { useState } from "react";

interface OptimizedImageProps extends Omit<ImageProps, "src"> {
  src: string;
  fallbackSrc?: string;
}

export function OptimizedImage({
  src,
  fallbackSrc = "/images/placeholder.png",
  alt,
  className,
  ...props
}: OptimizedImageProps) {
  const [imageSrc, setImageSrc] = useState(src);

  // For data URLs (base64 images from camera/file upload)
  if (src.startsWith("data:")) {
    return (
      <img
        src={src}
        alt={alt}
        className={className}
        {...(props as React.ImgHTMLAttributes<HTMLImageElement>)}
      />
    );
  }

  return (
    <Image
      src={imageSrc}
      alt={alt}
      className={className}
      onError={() => {
        setImageSrc(fallbackSrc);
      }}
      {...props}
    />
  );
}
