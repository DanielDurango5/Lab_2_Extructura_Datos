package org.example;

import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.file.Files;
import java.nio.file.Path;

public class Main {

    private static final String USERS_FILE = "user.dat";
    private static final String INDEX_FILE = "index.dat";

    private static final int NUM_BUCKETS = 100;
    private static final long NULL_PTR = -1;

    private static final long NODE_SIZE = 8 + 8 + 8;
    private static final long BUCKED_AREA_SIZE = (long) NUM_BUCKETS * 8;


    public static void main(String[] args) throws IOException {
        resetFiles();
        initializeIndexFile();
        addUser(1111L, "Pedro");
        addUser(1211L, "Luis");
        addUser(1212L, "Luisa");
        searchWithOutIndex(1212L);
        searchWithIndex(1212L);
    }

    private static int hash(long cc) {
        return (int) (Math.abs(cc) % NUM_BUCKETS);
    }

    private static void resetFiles() throws IOException {
        Files.deleteIfExists(Path.of(USERS_FILE));
        Files.deleteIfExists(Path.of(INDEX_FILE));
    }

    private static void initializeIndexFile() throws IOException{
        try (RandomAccessFile index = new RandomAccessFile(INDEX_FILE, "rw")){
            for (int i = 0; i < NUM_BUCKETS; i++) {
                index.writeLong(NULL_PTR);
            }
        }
    }

    private static void addUser(long cc, String name) throws IOException {
        long recordOffset;

        try (RandomAccessFile users = new RandomAccessFile(USERS_FILE, "rw")) {
            recordOffset = users.length();
            users.seek(recordOffset);

            users.writeLong(cc);
            users.writeUTF(name);
        }
        int bucket = hash(cc);

        try (RandomAccessFile index = new RandomAccessFile(INDEX_FILE, "rw")) {
        long bucketsPos = (long) bucket * 8;

        // Ir a la cabeza del bucket
        index.seek(bucketsPos);
        long oldHead = index.readLong();

        //Agregamos el nodo al final
        long newNodeOffSet = index.length();
        index.seek(newNodeOffSet);

        index.writeLong(cc);
        index.writeLong(recordOffset);
        index.writeLong(oldHead);

        index.seek(bucketsPos);
        index.writeLong(newNodeOffSet);

        System.out.printf(
                "Dato insertado: CC %d | Nombre: %s | Bucket: %d | RecordOffset: %d | NodeOffset: %d | oldHead: %d%n",
                cc, name, bucket, recordOffset, newNodeOffSet, oldHead);
        }
    }

    private static void searchWithOutIndex(long ccToFind) throws IOException {
        long start = System.nanoTime();
        int comparisons = 0;
        boolean found = false;

        try (RandomAccessFile users = new RandomAccessFile(USERS_FILE, "r")) {
            while (users.getFilePointer() < users.length()) {
                long cc = users.readLong();
                String name = users.readUTF();
                comparisons++;

                if (cc == ccToFind) {
                    found = true;
                    System.out.println("Lo encontramos!!");
                    System.out.println("CC: " + cc);
                    System.out.println("Nombre: "+ name);
                    System.out.println("Comparaciones: " + comparisons);
                    long end = System.nanoTime();
                    printTime(start, end);
                    break;
                }
            }
            if (!found) {
                System.out.println("No pudimos encontrar el dato");
                System.out.println("Comparaciones: " + comparisons);
                long end = System.nanoTime();
                printTime(start, end);
            }
        }
    }


    private static void searchWithIndex(long ccToFind) throws IOException {
        long start = System.nanoTime();
        int comparisons = 0;

        int bucket = hash(ccToFind);

        try (RandomAccessFile index = new RandomAccessFile(INDEX_FILE, "r");
             RandomAccessFile users = new RandomAccessFile(USERS_FILE, "r")) {

            long bucketPos = (long) bucket * 8;
            index.seek(bucketPos);

            long currentNodeOffset = index.readLong();

            while (currentNodeOffset != NULL_PTR) {
                index.seek(currentNodeOffset);

                long cc = index.readLong();
                long recordOffset = index.readLong();
                long nextOffset = index.readLong();

                comparisons++;

                if (ccToFind == cc) {
                    users.seek(recordOffset);
                    long foundCc = users.readLong();
                    String foundName = users.readUTF();
                    System.out.println("Lo encontramos usando indice!!!!!!");
                    System.out.println("CC: " + foundCc);
                    System.out.println("Nombre: " + foundName);
                    System.out.println("Comparaciones: " + comparisons);

                    long end = System.nanoTime();

                    printTime(start, end);
                    return;
                }

                currentNodeOffset = nextOffset;

            }

            System.out.println("No pudimos encontrar el dato usando indice");
            System.out.println("Comparaciones: " + comparisons);
            long end = System.nanoTime();
            printTime(start, end);

        }

    }

    private static void printTime(long start, long end){
        long nanos = end - start;
        double millis = nanos / 1_000_000.0;

        System.out.println("Tiempo: " + nanos + " ns");
        System.out.println("Tiempo: " + millis + " ms");
    }
}
