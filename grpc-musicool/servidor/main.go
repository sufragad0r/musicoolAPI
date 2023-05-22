package main

import (
	"google.golang.org/grpc"
	pb "grpc-musicool/proto/protobuf" // Importa el paquete generado por protoc
	"grpc-musicool/utilidades"
	"io"
	"log"
	"net"
	"os"
	"path/filepath"
)

type servidor struct {
	pb.UnimplementedStreamerServer
}

func (s *servidor) Audio(stream pb.Streamer_AudioServer) error {
	song, err := stream.Recv()
	utilidades.Chk(err)
	cancion := song.NombreCancion
	artista := song.NombreArtista
	album := song.Album
	filesPath := "../Biblioteca" + "/" + artista + "/" + album
	mp3File, errorObtenerMp3 := getMP3File(filesPath, &cancion)
	if errorObtenerMp3 != nil {
		log.Printf("Error al encontrar la cancion en el servidor: %v", errorObtenerMp3)
		return errorObtenerMp3
	}
	file, errorAbrirMp3 := os.Open(mp3File)
	if errorAbrirMp3 != nil {
		log.Printf("Error al abrir el archivo de la cancion: %v", errorAbrirMp3)
		return errorAbrirMp3
	}
	defer file.Close()
	buf := make([]byte, 8*1024*1024) // Ajusta el tamaño del búfer según tus necesidades
	for {
		n, err := file.Read(buf)
		if err != nil {
			if err != io.EOF {
				log.Printf("Error al leer el archivo podria estar fragmentado: %v", err)
			}
			break
		}
		//log.Printf(string(buf[:n]))
		log.Println(len(buf[:n]))

		data := &pb.Data{
			Sequence: 0, // Asigna un valor adecuado para el campo Sequence
			Filename: mp3File,
			Rate:     0, // Asigna un valor adecuado para el campo Rate
			Channels: 0, // Asigna un valor adecuado para el campo Channels
			Data:     buf[:n],
		}

		if err := stream.Send(data); err != nil {
			log.Printf("Error al enviar los datos al cliente: %v", err)
			break
		}
	}
	return nil
}

// Función para obtener la lista de archivos MP3 en la carpeta
func getMP3File(folderPath string, nombreCancion *string) (string, error) {
	var mp3File string

	err := filepath.Walk(folderPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if !info.IsDir() && info.Name() == *nombreCancion+".mp3" {
			mp3File = path
			return filepath.SkipDir
		}

		return nil
	})

	if err != nil {
		return "", err
	}

	if mp3File == "" {
		return "", nil
	}

	return mp3File, nil
}
func main() {
	listener, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Error al iniciar el listener: %v", err)
	}

	server := grpc.NewServer()
	pb.RegisterStreamerServer(server, &servidor{})

	// Inicia el servidor gRPC
	log.Println("Iniciando el servidor gRPC...")
	if err := server.Serve(listener); err != nil {
		log.Fatalf("Error al iniciar el servidor gRPC: %v", err)
	}
}
